# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

import datetime
from sqlalchemy import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def number_format(n):
    if n < 10:
        return '0' + str(n)
    return str(n)


class FileType(Enum):
    TV = 0
    Film = 1
    Anime = 2
    Ponies = 3
    Music = 4
    TVBroadCast = 5
    Software = 6
    nothing = 400
    All = 401


class Movie(Base):
    __tablename__ = 'Movie'

    id = Column(Integer, primary_key=True)
    tmdb = Column(Integer)
    title = Column(String, nullable=False)
    year = Column(Integer)
    added = Column(DateTime, default=datetime.datetime.now)

    popularity = Column(Float)
    vote = Column(Float)
    poster = Column(String)
    overview = Column(String)
    type = Column(Integer, default=FileType.Film)

    xdcc_packet = relationship('XDCCPackage', backref='Movie')
    episodes = relationship('TVShowEpisode', backref='Movie')

    # UniqueConstraint(tmdb)    # Because One movie can be in multiple language
    UniqueConstraint(title, year)

    def __repr__(self):
        if self.type == FileType.Film:
            return "<Movie(id='" + str(self.id) + "', title='" + str(self.title) + "', tmdb='" + str(self.tmdb) + "')>"
        else:
            return "<TVShow(id='" + str(self.id) + "', title='" + str(self.title) + "', tmdb='" + str(self.tmdb) + "')>"


class TVShowEpisode(Base):
    __tablename__ = 'TVShowEpisode'

    id = Column(Integer, primary_key=True)
    title_id = Column(Integer, ForeignKey('Movie.id'))
    season = Column(Integer)
    episode = Column(Integer)

    UniqueConstraint(title_id, season, episode)
    xdcc_packet = relationship('XDCCPackage', backref='TVShowEpisode')
    title = relationship('Movie', backref='TVShowEpisode')

    def __repr__(self):
        return "<Episode(id='" + str(self.id) + "', title='" + str(self.title.title) +\
               "', S" + str(number_format(self.season)) + \
                  "E" + str(number_format(self.episode)) + ")>"


class XDCCServer(Base):

    __tablename__ = 'XDCCServer'

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=False)
    port = Column(Integer, default=6667)
    ssl = Column(Boolean, default=False)
    UniqueConstraint(url, ssl)
    channel = relationship('XDCCChannel', backref='XDCCServer')

    def __repr__(self):
        return "<XDCCServer(id='" + str(self.id) + "', address='" + str(self.url) + "' ssl='" + str(self.ssl) + "')>"


class XDCCChannel(Base):
    __tablename__ = 'XDCCChannel'

    id = Column(Integer, primary_key=True)
    channel = Column(String, nullable=False)
    xdcc_server = Column(Integer, ForeignKey('XDCCServer.id'))
    server = relationship('XDCCServer', backref='XDCCChannel')

    def __repr__(self):
        return "<XDCCChannel(id='" + str(self.id) + "', address='" + str(self.server.url) + "@" + str(self.channel) + "')>"


class XDCCPackage(Base):
    __tablename__ = 'XDCCPackage'

    id = Column(Integer, primary_key=True)
    bot = Column(String, nullable=False)
    pkg = Column(Integer, nullable=False)
    # Nul if it is a TVShow
    movie_id = Column(Integer, ForeignKey('Movie.id'))
    movie = relationship('Movie', backref='XDCCPackage')
    # Nul if it is a Movie
    episode_id = Column(Integer, ForeignKey('TVShowEpisode.id'))
    episode = relationship('TVShowEpisode', backref='XDCCPackage')

    # Extracted Tags
    info = Column(String)
    # Package Size
    size = Column(String)
    # Orignal Title
    original_title = Column(String)

    last_updated = Column(DateTime, onupdate=datetime.datetime.now, default=datetime.datetime.now)

    # Make Server Accessible through Package
    # This can make things easier it also does a lot of things that you cant check
    # UNIQUE constraint failure
    # server = relationship('XDCCServer', backref='XDCCPackage')
    # network = Column(Integer, ForeignKey('XDCCServer.id'), nullable=False)

    # channel_id = Column(Integer, ForeignKey('XDCCChannel.id'), nullable=False)
    # channel = relationship('XDCCChannel', backref='XDCCPackage')

    # This is easier but will make the db bigger
    channel = Column(String)
    server = Column(String)

    UniqueConstraint(bot, pkg, server, channel)

    def __repr__(self):
        return "<XDCCPackage(id='" + str(self.id) + "', bot='" + str(self.bot) + "', pkg='" + str(self.pkg) \
               + "', last updated='" + str(self.last_updated) + "', movie='" + str(self.movie) + "')>"

from sqlalchemy.orm import sessionmaker


def create_db(engine):
    # Create The DB
    Base.metadata.create_all(engine)
    # # Create a Session
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == '__main__':

    import os

    egn = create_engine('sqlite:///test.db', echo=True)

    session = create_db(egn)

    r = session.query(Movie).all()

    for i in r:
        print(i.xdcc_packet[0].server)

    session.close()

    os.remove('test.db')

