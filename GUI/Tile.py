# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from PyQt4.Qt import *
from Database.database_definition import *


class Tile(QPushButton):
    """ Tile of a TileWall Displaying Movie's Poster, title, date and Rating"""

    def __init__(self, movie, size=154, type=FileType.Film):
        super(Tile, self).__init__()

        layout = QVBoxLayout()
        self.dat = movie

        l = QWebView()
        if movie.poster is not None:
            l.load(QUrl('http://image.tmdb.org/t/p/w' + str(size) + movie.poster))
        else:
            l.load(QUrl('img/default.jpg'))
        l.setFixedSize(154, 231)

        # Prevent the QWebView from grabbing Mouse control
        # Which makes user scream and makes PyQt exit with an error
        l.setEnabled(False)
        l.page().mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

        title = QLabel(movie.title)
        title.setAlignment(Qt.AlignCenter)

        vote = QHBoxLayout()
        vote.addWidget(QLabel(str(movie.year)), 0, Qt.AlignLeft)
        vote.addWidget(QLabel(str(movie.vote)), 0, Qt.AlignRight)

        layout.addWidget(title)
        layout.addWidget(l)
        layout.addLayout(vote)

        self.setLayout(layout)

    def sizeHint(self):
        return QSize(154 + 20, 231 + 60)

    def open_info(self, function):
        self.connect(self, SIGNAL('clicked()'), lambda: function(self.dat))