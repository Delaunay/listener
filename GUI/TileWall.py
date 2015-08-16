# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from GUI.Tile import *


def do_nothing(x):
    return


class TileWall(QScrollArea):

    def __init__(self, db=None, show_button=False):
        super(TileWall, self).__init__()
        self.type = FileType.Film
        self.tile_per_row = 6

        self.row = 1
        self.col = -1

        self.container = QWidget()
        self.layout = QGridLayout()

        self.container.setLayout(self.layout)
        self.setWidget(self.container)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignCenter)
        self.layout.setAlignment(Qt.AlignCenter)

        self.enable_resize_reload = False
        self.movie = None
        self.info = []

        self.db = db
        self.push_button_action = do_nothing
        self.show_button = show_button

        if show_button:
            self.latest_switch = QPushButton('Latest')
            self.popular_switch = QPushButton('Popular')
            self.best_switch = QPushButton('Best')

            sl = QHBoxLayout()
            sl.addWidget(self.latest_switch)
            sl.addWidget(self.popular_switch)
            sl.addWidget(self.best_switch)
            self.layout.addLayout(sl, 0, 0, 1, self.tile_per_row)

    def latest_button(self, function):
        if self.show_button:
            self.connect(self.latest_switch, SIGNAL('clicked()'), function)

    def popular_button(self, function):
        if self.show_button:
            self.connect(self.popular_switch, SIGNAL('clicked()'), function)

    def best_button(self, function):
        if self.show_button:
            self.connect(self.best_switch, SIGNAL('clicked()'), function)

    def load_movies(self, movie=None):
        self.movie = movie

        for i in range(0, len(movie)):
            p = Tile(self.movie[i], type=self.type)
            p.open_info(self.push_button_action)
            self.add_poster(p)

    def add_poster(self, poster):

        if self.col < self.tile_per_row - 1:
            self.col += 1
        else:
            self.col = 0
            self.row += 1

        self.layout.addWidget(poster, self.row, self.col)
        self.container.resize(self.layout.sizeHint())

    def search(self, search, t=FileType.Film, n=48):

        # search = string.capwords(search)
        s = search.split(' ')

        if t == FileType.All or t is None:
            query = self.db.query(Movie)
        else:
            query = self.db.query(Movie).filter(Movie.type == t)

        if s[0] != '':
            for i in s:
                query = query.filter(func.instr(func.upper(Movie.title), func.upper(i)))

        return query.limit(n).all()

    def resizeEvent(self, QResizeEvent):
        super(TileWall, self).resizeEvent(QResizeEvent)

    def reload(self):
        self.load_movies(self.movie)

    def popular(self, n=48):
        return self.db.query(Movie).filter(Movie.type == self.type).order_by(Movie.popularity.desc()).limit(n).all()

    def latest(self, n=48):
        return self.db.query(Movie).filter(Movie.type == self.type).order_by(Movie.added.desc()).limit(n).all()

    def best(self, n=48):
        return self.db.query(Movie).filter(Movie.type == self.type).order_by(Movie.vote.desc()).limit(n).all()

    def load_default(self):
        self.load_popular()

    def load_popular(self):
        if self.show_button:
            self.popular_switch.setCheckable(True)
            self.popular_switch.setChecked(True)
        self.load_movies(self.popular())

    def load_best(self):
        if self.show_button:
            self.best_switch.setCheckable(True)
            self.best_switch.setChecked(True)
        self.load_movies(self.best())

    def load_latest(self):
        if self.show_button:
            self.latest_switch.setCheckable(True)
            self.latest_switch.setChecked(True)
        self.load_movies(self.latest())

    def sizeHint(self):
        return self.container.sizeHint()

        # def _reset(self):
    #     self.row = 1
    #     self.col = -1
    #
    #     self.layout = QGridLayout()
    #
    #     self.sl = QHBoxLayout()
    #     self.sl.addWidget(self.latest_switch)
    #     self.sl.addWidget(self.popular_switch)
    #     self.sl.addWidget(self.best_switch)
    #     self.layout.addLayout(self.sl, 0, 0, 1, self.tile_per_row)
    #
    #     self.container = QWidget()
    #     self.layout.setAlignment(Qt.AlignCenter)
    #     self.container.setLayout(self.layout)
    #     self.setWidget(self.container)


class MovieWidget(TileWall):

    def __init__(self, db=None, show_button=False):
        super(MovieWidget, self).__init__(db, show_button)


class TVShowWidget(TileWall):

    def __init__(self, db=None, show_button=False):
        super(TVShowWidget, self).__init__(db, show_button)
        self.type = FileType.TV


class PoniesWidget(TileWall):

    def __init__(self, db=None, show_button=False):
        super(PoniesWidget, self).__init__(db, show_button)
        self.type = FileType.Ponies


if __name__ == '__main__':

    import sys
    from GUI.style import set_style

    QApplication.setStyle(QStyleFactory.create('Plastique'))
    app = QApplication(sys.argv)

    set_style(app)

    db = 'C:/ZenBBData/my_db.db'
    engine = create_engine('sqlite:///' + db, echo=False)
    db = create_db(engine)

    main = TileWall(db)
    main.load_default()
    # main.tile_per_row = 10
    # main.reload()
    main.show()

    set_style(app)

    sys.exit(app.exec_())