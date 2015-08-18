# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

import irc.client
import functools
import irc.connection
import ssl as mod_ssl
import time
import random as rand
from XDCC.DCCConnection import *


class IRCChat():
    """ less Simple IRC Client
            - Multiple Servers  (SSL or Not)
            - Multiple DCC      (No SSL)
            - DCC Custom Queue
            - I need to wait for the ping
            -> sometimes ping is not received and we must force the server to send it by sending a ping
    """

    def __init__(self):

        # IRC Stuff
        #==========================================

        # Removes Errors about decoding UTF8
        irc.client.ServerConnection.buffer_class.errors = 'replace'
        self.reactor = irc.client.Reactor()

        # Multiple Connection
        self.server_connection = {}
        self.connection_to_server = {}

        # DCC Stuff
        self.download_folder = 'C:/ZenBBData/downloads/'

        # DCC active bot with external download Queue
        # because XDCC Queue is limited to 2-3 Queued item
        self.dcc_bot = {}       # IP to DCCConnection object
        self.dcc_queue = {}     # Bot to xdcc message

        # Callbacks setup
        self.download_starting_callback = lambda dcc_connection, info: None
        self.download_progress_callback = lambda dcc_connection, info: None
        self.download_end_callback = lambda dcc_connection, info: None

        # ping need to be received before sending commands
        self.reactor.add_global_handler("all_events", self._dispatcher, -10)

    def _dispatcher(self, connection, event):
        """ Dispatch events to on_<event.type> method, if present.  """
        do_nothing = lambda c, e: None
        method = getattr(self, "on_" + event.type, do_nothing)
        method(connection, event)

    def on_ping(self, c, e):
        self.re_join(c.server)

    def on_welcome(self, c, e):
        self.re_join(c.server)

    def on_motd(self, c, e):
        pass
        # self.re_join(c.server)

    # def on_endofmotd(self, c, e):
    #     self.ping_received = True

    @staticmethod
    def nick_gen(length=5):

        upper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        number = '1234567890'
        lower = upper.lower()

        letter = upper + lower
        all = letter + number
        n = ''
        m = len(all)
        for i in range(0, length):
            n += all[rand.randint(0, m - 1)]

        return letter[rand.randint(0, len(letter) - 1)] + n

    def add_connection(self, server, nick, port=6667, ssl=False):

        nick = self.nick_gen()

        if not server in self.server_connection:
            s = self.reactor.server()
            if ssl:
                wrapper = functools.partial(mod_ssl.wrap_socket)
                s.connect(server, port, nick, connect_factory=irc.connection.Factory(wrapper=wrapper))
            else:
                s.connect(server, port, nick)

            self.server_connection[s.server] = {'server': s, 'channel': set(), 'ready': False}
            # self.connection_to_server[str(s)] = s.server

            return s

    def reconnect(self, server):
        """ Reconnect to server connection and rejoin every channel"""

        # Check if we are connected:
        if not self.is_connected(server):
            # try to reconnect
            self.server_connection[server]['server'].reconnect()
            self.re_join(server)

    def re_join(self, server):
        if 'old_channel' in self.server_connection[server]:
            for i in self.server_connection[server]['old_channel']:
                self.join_channel(server, i)

            del self.server_connection[server]['old_channel']

    def join_pending(self, server):
        if 'pending_channel' in self.server_connection[server]:
            for i in self.server_connection[server]['pending_channel']:
                self.join_channel(server, i)

            del self.server_connection[server]['pending_channel']

    def join_channel(self, server, channel):
        if self.server_connection[server]['ready']:
            self.server_connection[server]['server'].join(channel)

        if 'pending_channel' in self.server_connection[server]:
            self.server_connection[server]['pending_channel'].add(channel)
        else:
            self.server_connection[server]['pending_channel'] = set(channel)

    def has_joined(self, server, channel):
        return channel in self.server_connection[server]['channel']

    def is_connected(self, server):
        return server in self.server_connection and self.server_connection[server]['server'].connected is True

    def public_message(self, server, channel, msg):
        self.server_connection[server].privmsg(channel, msg)

    def private_message(self, server, nick, msg):
        self.server_connection[server]['server'].privmsg(nick, msg)

    def server_connection(self, server):
        return self.server_connection[server]['server']

    def disconnect_all(self):
        self.reactor.disconnect_all()

    def request_dcc_packet(self, server, bot, pkg, channel=None, info=None):
        """ Current Download are queued. If connection is lost we can resume download
            return the number of item queued, 0 mean that the download will start right away

            info: holds user defined information
        """
        print('Requesting Packet')

        # Check if server is known
        if not server in self.server_connection:
            raise irc.client.ServerConnectionError('Unknown Server')

        # Check if we are connected: if not tries to reconnect
        # and rejoin every channel it was before
        self.reconnect(server)

        # Check if we are in the required Channel:
        if channel is not None:
            self.join_channel(server, channel)

        # Check bot key exist
        if bot in self.dcc_queue:
            self.dcc_queue[bot].append(('xdcc send ' + str(pkg), info))
        else:
            self.dcc_queue[bot] = [('xdcc send ' + str(pkg), info)]

        # the bot is not busy
        l = len(self.dcc_queue[bot])
        if l == 1:
            print('Download Message Sent')
            # Start download
            self.private_message(server, bot, self.dcc_queue[bot][0][0])

        return l - 1

    def start(self):
        self.reactor.process_forever()

    # Channel Management
    #=========================

    def on_join(self, c, e):
        if 'pending_channel' in self.server_connection[c.server]:
            if e.target in self.server_connection[c.server]['pending_channel']:
                self.server_connection[c.server]['pending_channel'].remove(e)

        if not e.target in self.server_connection[c.server]['channel']:
            self.server_connection[c.server]['channel'].add(e.target)

    def on_disconnect(self, c, e):
        self.ping_received = False
        # When we are disconnected we leave all channel we should take those into account
        # Save old channel for rejoin
        self.server_connection[c.server]['old_channel'] = self.server_connection[c.server]['channel']

        # Erase joined channel
        self.server_connection[c.server]['channel'] = set()

    # DCC Events
    #=========================

    def on_ctcp(self, c, e):
        """ GUI Instance will be created here """

        if len(e.arguments) > 1:
            print('DCC Connection')

            with self.reactor.mutex:
                dcc = DCCConnection(self.reactor, dcctype='raw')
                self.reactor.connections.append(dcc)

            dcc.download_end_callback = self.download_end_callback
            dcc.download_starting_callback = self.download_starting_callback
            dcc.download_progress_callback = self.download_progress_callback

            # e.target = My Nick    e.source = bot Name
            dcc.name = e.source.split('!')[0]
            dcc.server = c.server
            dcc.connection_set_up(c, e, self.download_folder, self.dcc_queue[dcc.name][0][1])

            self.dcc_bot[dcc.name] = dcc

    def on_dccmsg(self, c, e):
        # handles itself
        c.receive_bytes(c, e, self.dcc_queue[c.name][0][1])

    def on_dcc_disconnect(self, c, e):

        # check for timeout
        if len(e.arguments) > 0 and e.arguments[0] == 'Connection reset by peer':
            pass
        else:
            # remove from  current download
            c.close_download(c, e, self.dcc_queue[c.name][0][1])

    def on_all_raw_messages(self, c, e):
        print(e.arguments)

    def on_endofmotd(self, c, e):
        self.server_connection[c.server]['ready'] = True
        self.join_pending(c.server)

    # fwef
    def on_privnotice(self, c, e):

        # Server receive Sever info as privnotice
        # Sever can join channel
        info = e.arguments[0]
        # bot = e.source.split('!')[0]

        if info.find('Sending') > -1:
            # remove from task
            print('=======|> Sending Acknowledge')

        if info.find('Completed') > -1:
            print('=======|> End')

            bot = e.source.split('!')[0]
            self.send_out_queued_item(bot, self.dcc_bot[bot].server)
            del self.dcc_bot[bot]
            # remove from open dcc connection

    def send_out_queued_item(self, bot, server):

        # if another item is Queued
        if len(self.dcc_queue[bot]) > 1:
            print('Queue', self.dcc_queue)
            self.dcc_queue[bot].pop(0)

            print('Download Message Sent')
            self.private_message(server, bot, self.dcc_queue[bot][0][0])
        # the queue is empty
        else:
            print('No Queue', self.dcc_queue)
            self.dcc_queue[bot].pop(0)


if __name__ == '__main__':

    import sys

    a = IRCChat()
    a.add_connection('irc.otaku-irc.fr', 'otc_nick3', 6601, True)
    # a.add_connection('irc.criten.net', 'cri_nick4')
    # a.join_channel('irc.criten.net', '#elitewarez')

    a.join_channel('irc.otaku-irc.fr', '#serial_us')
    time1 = time.time()
    time2 = time.time()
    request = False

    while True:

        time2 = time.time()
        a.reactor.process_once()

        #if a.is_connected('irc.otaku-irc.fr'):
        #    print(a.server_connection['irc.otaku-irc.fr'])

        if time2 - time1 > 2:
            time1 = time.time()
            # print(a.is_connected('irc.otaku-irc.fr'))

            if a.has_joined('irc.otaku-irc.fr', '#serial_us'):
                print('Join !')
                request = True
            else:
                print('here')
                # a.join_channel('irc.otaku-irc.fr', '#serial_us')