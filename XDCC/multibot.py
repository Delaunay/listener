# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

import string
import irc.client
# from package import *
import sys
from enum import Enum
import re
from Database.database_definition import *
import string
from XDCC.IRCChat import *


def printable(st):
    return ''.join(filter(lambda x: x in string.printable, st))


def extract_info_from_title(name):

        rg = re.compile(r'(?ix)(.*)\.(xxx)')
        r = rg.split(name)[1:]
        if len(r) != 0:
            return FileType.Ponies, r

        # \.(.*)\.(\d{3,})p\.(.*)\.(.*)\.(.*)
        rg = re.compile(r'(?ix)(.*)\.(S\d{2})(E\d{2})')

        # TV Regex
        r = rg.split(name)[1:]
        if len(r) != 0:
            return FileType.TV, r

        # Movie (YYYY)
        rg = re.compile(r'(?ix)(.*)\..?(\d{4}?).?')
        r = rg.split(name)[1:]
        if len(r) != 0:
            return FileType.Film, r

        # Movie

        # Pack Complete.Season.1
        # rg = re.compile(r'(?ix)(.*)\.(S\d{2})')

        # Super pack Season.4-5

        # Anime name.E000
        # rg = re.compile(r'(?ix)(.*)\.(E\d{2,3})')

        # Any other stuff is considered a Software

        # Music MP3 FLAC LOSSLESS

        # TVEmission    HDTV

        # print(name)
        return None, None


class MultiBot():

    def __init__(self, connection):
        """ Connection are XDCCServer list"""

        # Removes Errors about decoding UTF8
        irc.client.ServerConnection.buffer_class.errors = 'replace'

        # Connection
        # self.reactor = irc.client.Reactor()
        self.irc = IRCChat()

        print("Connecting...")
        self.connection = dict()

        # So we can get on which channel it was sent
        for i in connection:
            self.connection[str(self.add_connection(i.url, i.port, i.ssl, i.channel))] = i

        print("Connected")

        self.active_connection = 0
        self.irc.reactor.add_global_handler("all_events", self._dispatcher, -10)
        self.callback = None

    def _dispatcher(self, connection, event):
        """ Dispatch events to on_<event.type> method, if present.  """
        do_nothing = lambda c, e: None
        method = getattr(self, "on_" + event.type, do_nothing)
        # print(event.type)
        method(connection, event)

    def on_disconnect(self, c, e):
        cc = str(c)
        cc = self.connection[cc]
        self.active_connection -= 1
        print("Disconnected from " + str(cc.channel) + '@' + str(cc.url))
        print(e.arguments[0])

        # if e.arguments[0] == 'Connection reset by peer':
        #     # self.add_connection(cc.url, cc.port, cc.channel, 'Amenirdis2')
        #     c.connect(cc.url, cc.port, 'Amenirdis2')
        #     c.join(cc.channel)
        #     self.active_connection += 1
        # else:
            # del self.connection[str(c)]

        # if self.active_connection == 0:
        #     sys.exit()

    def add_connection(self, url, port=6667, ssl=False, channel=[]):

        attemp = 0

        while attemp < 1:
            try:
                #r = self.reactor.server()
                #r.connect(server, port, nickname)

                if ssl is False:
                    r = self.irc.add_connection(server=url, nick='Amenirdis', port=6667, ssl=False)
                else:
                    r = self.irc.add_connection(server=url, nick='Amenirdis', port=port, ssl=ssl)

                print("    Conected to: " + url)

                for i in channel:
                    self.irc.join_channel(url, i)
                    print('        ' + str(i))

                return r

            except irc.client.ServerConnectionError as e:
                print("    Fail : " + url)
                print('        ' + str(e))
                attemp += 1

        return None

    def on_pubmsg(self, c, e):

        if self.callback is not None:
            a = printable(e.arguments[0]).split()

            if len(a) >= 4 and a[0][1:].isdigit():
                cc = str(c)
                cc = self.connection[cc]

                # Get Which file type it belong
                file_type, name = extract_info_from_title(a[-1])

                # print(name, file_type)

                if name is not None and len(name) > 0:   # file_type is not None

                    if file_type == FileType.Film or file_type == FileType.Ponies:
                        # print(name)
                        p = {
                            'bot': e.source.split('!')[0],
                            'pkg': a[0][1:],
                            'server': cc.url,
                            'title': string.capwords(name[0].replace('.', ' ')),    # Format the title
                            'year': None,
                            'info': name[1:],
                            'original_title': e.arguments[0],
                            'size': a[-2][1:-1],
                            'channel': e.target
                        }

                        if len(name) > 1:
                            if file_type == FileType.Film:
                                p['year'] = name[1]
                            p['info'] = name[2:]

                        self.callback(p, file_type)

                    elif file_type == FileType.TV:

                        p = {
                            'bot': e.source.split('!')[0],
                            'pkg': a[0][1:],
                            'server': cc.url,
                            'title': string.capwords(name[0].replace('.', ' ')),
                            'season': int(name[1][1:]),
                            'episode': int(name[2][1:]),
                            'year': None,
                            'info': name[3:],
                            'original_title': e.arguments[0],
                            'size': a[-2][1:-1],
                            'channel': e.target,
                        }

                        self.callback(p, FileType.TV)

                    else:
                        print('Skipped Packet')

    def start(self):
        self.irc.reactor.process_forever()

from tmdb import *


class CallBack():
    k = 0
    info = TMDbAPY("844238e82e0809bc08bb0d3c1d0842aa")

    @staticmethod
    def check(t, y, type, s):
        if type == FileType.Film:
            return s.query(Movie).filter(and_(Movie.title == t, Movie.year == y, Movie.type == type)).all()
        else:
            return s.query(Movie).filter(and_(Movie.title == t, Movie.type == type)).all()

    def add_packet(self, p, s, type=FileType.Film):

            # Check Movie
            movie = self.check(p['title'], p['year'], type, s)

            if type == FileType.Film or type == FileType.Ponies:
                get_info = lambda x, y, z: self.info.movie_search(x, y, z)
            else:
                get_info = lambda x, y, z: self.info.tv_search(x, y)

            if len(movie) > 0:      # Movie Exists
                m = movie[0]

                if m.overview is None:
                    # Get Movie info
                    r = get_info(m.title, m.year, type == FileType.Ponies)

                    if r is not None and len(r) > 0:

                        if FileType.Ponies == type:
                            for i in r:
                                if i['adult']:
                                    r = i
                                    break
                            else:
                                r = None
                        else:
                            r = r[0]

                        if r is not None:
                            # if type == FileType.TV:
                            #     m.title = r["original_name"]    # Make one with any Movie that are considered the same
                            # elif type == FileType.Film:
                            #     m.title = r["original_title"]
                            # else:
                            m.title = p["title"]
                            #
                            m.overview = r['overview']
                            m.popularity = float(r['popularity'])
                            m.tmdb = int(r['id'])
                            m.poster = r["poster_path"]
                            m.vote = float(r['vote_average'])

                            s.flush()

                # print(m)

                # print('Loading Existing Movie: ' + str(m))
            else:
                # if not add it

                r = get_info(p['title'], p['year'], type == FileType.Ponies)

                if r is not None and len(r) > 0:
                    if FileType.Ponies == type:
                        for i in r:
                            if i['adult']:
                                r = i
                                break
                        else:
                            r = None
                    else:
                        r = r[0]

                    # if the movie title is in another language it will modify it
                    # people might download a foreign version of the movie

                    # # Check if the movie with the new title is present
                    # if type == FileType.TV:
                    #     ret = self.check(r['original_name'], p['year'], type, s)
                    #
                    # if type == FileType.TV and len(ret) > 0:      # Movie Exists on a different name
                    #     m = ret[0]
                    # else:


                    # Movie is new
                    m = Movie(title=p['title'], year=p['year'], type=type)

                    if r is not None:
                        m.title = p["title"]
                        m.overview = r['overview']
                        m.popularity = float(r['popularity'])
                        m.tmdb = int(r['id'])
                        m.poster = r["poster_path"]
                        m.vote = float(r['vote_average'])

                        if type == FileType.TV:
                            m.year = r['first_air_date']

                    s.add(m)
                    s.flush()
                else:
                    return

            # if it is a TVShow
            if type == FileType.TV:
                # Check if tv show exist already
                tv_pkg = s.query(TVShowEpisode).filter(and_(TVShowEpisode.title_id == m.id,
                                                            TVShowEpisode.season == p['season'],
                                                            TVShowEpisode.episode == p['episode'])).all()

                if len(tv_pkg) == 0:
                    tv = TVShowEpisode(title=m, season=p['season'], episode=p['episode'])
                    s.add(tv)
                    s.flush()
                else:
                    tv = tv_pkg[0]

            # Populate the movie.id
            if type == FileType.TV:
                print(tv)
            else:
                print(m)

            # Check Package
            pkg = s.query(XDCCPackage).filter(and_(XDCCPackage.bot == p['bot'],
                                                   XDCCPackage.pkg == p['pkg'],
                                                   XDCCPackage.server == p['server'])).all()

            if len(pkg) > 0:        # Package Exists
                # print('Updating Package: ' + str(pkg[0]))
                # Update Existing Packet
                pm = pkg[0]
                info = ''

                for i in p['info']:
                    info += i

                pm.info = info

                if type == FileType.Film:
                    pm.movie = m
                    pm.episode_id = 0
                elif type == FileType.TV:
                    pm.episode = tv
                    pm.movie_id = 0

                # print('Updated Package: ' + str(p))
            # if not we add the package to the db
            else:
                info = ''

                for i in p['info']:
                    info += i

                # print('Adding Package: ' + str(p))
                if type == FileType.Film or type == FileType.Ponies:
                    pa = XDCCPackage(bot=p['bot'], pkg=p['pkg'], server=p['server'], channel=p['channel'], movie=m)
                elif type == FileType.TV:
                    pa = XDCCPackage(bot=p['bot'], pkg=p['pkg'], server=p['server'], channel=p['channel'], episode=tv)
                else:
                    pa = XDCCPackage(bot=p['bot'], pkg=p['pkg'], server=p['server'], channel=p['channel'], movie=m)

                pa.info = info
                pa.size = p['size']
                pa.original_title = p['original_title']
                s.add(pa)

            s.flush()

            # Commit once in a while
            self.k += 1
            if self.k > 100:
                print('Commit')
                s.commit()
                self.k = 0


if __name__ == '__main__':

    db = 'C:/ZenBBData/my_db.db'
    import time

    import os
    from populate.irc_server import setup
    # #
    #os.remove(db)
    setup(db)

    # time.sleep(2*60)

    engine = create_engine('sqlite:///' + db, echo=False)
    s = create_db(engine)

    connection = s.query(XDCCServer).all()

    cb = CallBack()

    builder = MultiBot(connection)
    builder.callback = lambda p, y: cb.add_packet(p, s, y)

    try:
        builder.start()
    finally:
        s.commit()