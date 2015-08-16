# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

# from PyQt4.QtCore import *
# import PyQt4.QtGui as qw
# from PyQt4.Qt import *

from GUI.TileWall import *
from GUI.InfoWidget import *
from GUI.Manager import *
from GUI.Configuration import *
import time


class ZenBB(QMainWindow):
    """ The main widget is a StackedWidget. There are 6 Permanent Widget
    Currently only one Temporary Widget is supported since it is deleted after a new temporary is inserted
    This because there are not way the user could show those temporary once he changes view.
    The back action only takes the user back one view"""

    def __init__(self, db=None):
        super(ZenBB, self).__init__()

        self.db = db
        self.running = True

        # Main Movie Window for search and latest
        self.widget_movie = self.setup_tile_wall(FileType.Film, True)
        self.widget_tv = self.setup_tile_wall(FileType.TV, True)         # QPushButton('TV Show')

        # Modules window
        self.widget_manager = Manager()     # QPushButton('Manager')
        self.widget_planner = QPushButton('Planner')
        self.widget_config = Configuration()

        # Temporary window showing details about particular movie
        self.detail_widget = dict()

        # to be able to return to the previous window
        self.previous_widget = 0
        self.n_widget = 6

        # Search bar
        self.combo_box = QComboBox()
        self.combo_box.addItem('Movie')
        self.combo_box.addItem('TV')
        self.combo_box.addItem('All')

        self.combo_box_value = [FileType.Film, FileType.TV, FileType.Anime, FileType.All]

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search ...')
        self.search_bar.connect(self.search_bar, SIGNAL('returnPressed()'), self.search)

        self.main_window = self
        self.main_window.setWindowTitle('ZenBB')
        self.central_widget = QStackedWidget()
        self.main_window.setCentralWidget(self.central_widget)

        self.central_widget.addWidget(self.widget_movie)
        self.central_widget.addWidget(self.widget_tv)
        # self.central_widget.addWidget(self.widget_anime)
        self.central_widget.addWidget(self.widget_manager)
        self.central_widget.addWidget(self.widget_planner)
        self.central_widget.addWidget(self.widget_config)

        self.tool_bar = QToolBar()
        self.status_bar = QStatusBar()
        self.status_bar.showMessage('Version 0.0.0')
        self.main_window.addToolBar(self.tool_bar)
        self.main_window.setStatusBar(self.status_bar)

    def setup_tile_wall(self, ftype, show=False):
        r = TileWall(self.db, show)
        r.type = ftype

        r.push_button_action = self.open_info
        r.best_button(lambda: self.movie_action(FileType.Film, 'BEST'))
        r.latest_button(lambda: self.movie_action(FileType.Film, 'LAST'))
        r.popular_button(lambda: self.movie_action(FileType.Film, 'POP'))

        return r

    def movie_action(self, ftype, order):
        if self.central_widget.count() > self.n_widget:
            self.central_widget.removeWidget(self.central_widget.widget(self.n_widget))

        s = self.setup_tile_wall(ftype, True)
        self.central_widget.addWidget(s)

        if order == 'POP':
            s.load_popular()
        elif order == 'LAST':
            s.load_latest()
        elif order == 'BEST':
            s.load_best()

        self._update_central_widget(self.n_widget)

    def search(self):

        txt = self.search_bar.text()
        self.search_bar.setText('')

        if self.central_widget.count() > self.n_widget:
            self.central_widget.removeWidget(self.central_widget.widget(self.n_widget))

        s = MovieWidget(self.db)
        s.push_button_action = self.open_info
        self.central_widget.addWidget(s)

        s.load_movies(s.search(txt, self.combo_box_value[self.combo_box.currentIndex()]))
        self._update_central_widget(self.n_widget)

    def _update_central_widget(self, idx):
        self.previous_widget = self.central_widget.currentIndex()
        self.central_widget.setCurrentIndex(idx)

    def back(self):
        self._update_central_widget(self.previous_widget)

    def _add_toolbar_item(self, title, idx):
        action = QAction(title, self.tool_bar)
        action.connect(action, SIGNAL('triggered()'), lambda: self._update_central_widget(idx))

        if idx < 3:
            action.connect(action, SIGNAL('triggered()'), lambda: self.combo_box.setCurrentIndex(idx))
        self.tool_bar.addAction(action)

    def _set_tool_bar(self):
        self.tool_bar.setMovable(False)

        self._add_toolbar_item('Movies', 0)
        self._add_toolbar_item('TV Shows', 1)
        # self._add_toolbar_item('Anime', 2)
        self.tool_bar.addSeparator()

        self.tool_bar.addWidget(self.combo_box)
        self.tool_bar.addWidget(self.search_bar)
        back = QPushButton('Back')
        back.connect(back, SIGNAL('clicked()'), self.back)
        self.tool_bar.addWidget(back)

        self.tool_bar.addSeparator()

        self._add_toolbar_item('Manager', 3)
        self._add_toolbar_item('Planner', 4)
        self.tool_bar.addSeparator()
        self._add_toolbar_item('Configuration', 5)

    def download_action(self, packet, msg):
        self.widget_manager.add_download(packet)

    def open_info(self, movie):
        if self.central_widget.count() > self.n_widget:
            self.central_widget.removeWidget(self.central_widget.widget(self.n_widget))

        info = InfoWidget(movie, db=self.db)
        info.download_action_callback = self.download_action
        self.central_widget.addWidget(info)
        self._update_central_widget(self.n_widget)

    def start(self):
        # Splash Start
        splash = QSplashScreen(QPixmap('img/bsplash.png'))
        splash.show()

        # Loading and setting things up
        h = max(650, 640)
        self._set_tool_bar()

        self.main_window.setMinimumSize(16 * h / 9, h)

        # Movies
        splash.showMessage('Loading latest Movies', Qt.AlignCenter, Qt.white)
        self.widget_movie.load_default()

        # TV
        splash.showMessage('Loading latest TV Shows', Qt.AlignCenter, Qt.white)
        self.widget_tv.load_default()
        # time.sleep(1)

        # Anime
        splash.showMessage('Loading latest Anime', Qt.AlignCenter, Qt.white)
        # self.widget_anime.load_default()

        # time.sleep(1)

        # Splash End
        self.main_window.show()
        splash.finish(self.main_window)
        w = self.widget_movie.sizeHint().width()
        self.main_window.resize(w + 20, w * 9 / 16)

    def closeEvent(self, *args, **kwargs):
        self.running = False

if __name__ == '__main__':

    import sys
    from GUI.style import set_style

    QApplication.setStyle(QStyleFactory.create('Plastique'))
    app = QApplication(sys.argv)

    set_style(app)

    db = 'C:/ZenBBData/my_db.db'
    engine = create_engine('sqlite:///' + db, echo=False)
    db = create_db(engine)

    main = ZenBB(db)
    main.start()

    set_style(app)

    sys.exit(app.exec_())