# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

import string
import irc.client
from enum import Enum
import time
import shlex
import struct
import os


def printable(st):
    return ''.join(filter(lambda x: x in string.printable, st))

                #    2**10      2**20       2**30       10**3       10**6      10**9
speed_unit = dict(ko=1024, Mo=1048576, Go=1073741824, kb=1000, Mb=1000000, Gb=1000000000)


class DownloadState(Enum):
    RequestSent = 0             # ===> request_dcc_packet()
    RequestAcknowledged = 1     # ===> Private Notice ? This is where DownloadFailure is sent if any
    WaitingList = 2             # Set by
    DownloadInit = 3            # on_ctcp()
    DownloadStart = 4           # on_dccmsg()
    DownloadEnd = 5             # on_dcc_disconnect()


class DownloadFailure(Enum):
    RequestDenied = 0
    PacketAlreadyRequested = 0
    # ...


class DCCConnection(irc.client.DCCConnection):
    """ Makes DCC downloads manage themselves so the IRC client only manage what matters
        Thoughts:
            - There might be a problem when the user will be downloading multiple files (writing slow)

        Passive DCC is not supported. It makes users scream anyway
        Resume is not implemented
    """

    def __init__(self, r, dcctype='raw'):
        super(DCCConnection, self).__init__(r, dcctype)

        # for Time and Speed Measure
        self.total_size = 1             # Total Size we need to receive
        self.received_bytes = 0         # Bytes received
        self.start_time = time.time()   # Time at which the downloading started
        self.last_time = 0
        self.last_bytes = 0
        self.speed = 0
        self.k = 0
        self.file_name = ''
        self.resume = False
        self.file = None
        self.name = None    # bot name
        self.server = None
        self.user_defined = None
        self.state = None

          # Callbacks
        self.download_starting_callback = lambda dcc_connection, info: None
        self.download_progress_callback = lambda dcc_connection, info: None
        self.download_end_callback = lambda dcc_connection, info: None

    @staticmethod
    def new_dcc_connection(reactor, dcctype='raw'):

        with reactor.mutex:
            dcc = DCCConnection(reactor, dcctype=dcctype)
            reactor.connections.append(dcc)

        return dcc

    def open_file(self, file_name):
        self.file_name = file_name
        # Open the file
        # Resume Case
        self.resume = False
        if os.path.exists(file_name):
            # self.resume = True
            # self.received_bytes = os.path.getsize(file_name)
            # self.file = open(file_name, 'a')    # append mode

            # Need to be removed
            os.remove(file_name)
            self.file = open(file_name, "wb")
        else:
            self.file = open(file_name, "wb")

    def connection_set_up(self, c, e, df, info=None):

        payload = e.arguments[1]
        parts = shlex.split(payload)

        if len(parts) != 5:
            print('parts', parts)
        else:
            command, filename, peer_address, peer_port, size = parts

            self.total_size = int(size)
            self.start_time = time.time()
            self.last_time = time.time()
            self.open_file(df + filename)

            if command != "SEND":
                return

            peer_address = irc.client.ip_numstr_to_quad(peer_address)
            peer_port = int(peer_port)
            try:
                self.connect(peer_address, peer_port)
                self.download_starting_callback(self, info)
            except irc.client.DCCConnectionError as e:
                print('Error: ', e)

    def receive_bytes(self, dcc_connection, event, info=None):
        # Qts is going to update itself at least 25x per second
        # which make the speed updates itself every 2 seconds at least

        # if self.resume:     # ignore first bytes and tells
        #     self.resume = False
        #     self.send_bytes(struct.pack("!I", self.received_bytes))
        #     return

        if self.k > 50:
            self.last_bytes = self.received_bytes
            self.last_time = time.time()
            self.k = 0
            self.download_progress_callback(self, info)

        data = event.arguments[0]
        self.file.write(data)
        self.received_bytes += len(data)
        self.send_bytes(struct.pack("!I", self.received_bytes))
        self.k += 1

    def close_download(self, connection, event, info=None):
        if self.file is not None:
            self.file.close()
            self.download_end_callback(self, info)

    # Download Stats
    #===============================

    def file_size(self, div=1048576):
        """ File size (default: Mo) """
        return self.total_size / div

    def average_speed(self, div=1024):
        """ Overall speed :return speed (default: ko/s)"""
        self.speed = self.received_bytes / (time.time() - self.start_time)
        return self.speed / div

    def instant_speed(self, div=1024):
        """ Windowed average :return speed (default: ko/s)"""
        if self.speed > 0:
            return (self.received_bytes - self.last_bytes) / (time.time() - self.last_time) / div
        return 0

    def eta(self, div=60):
        """ :return ETA  Estimated Time to Arrival (default:Minutes)"""
        if self.speed > 0:
            return (self.total_size - self.received_bytes) / self.speed / div
        return 0

    def completed(self):
        return self.received_bytes / self.total_size
