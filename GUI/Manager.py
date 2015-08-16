# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from PyQt4.Qt import *
from Database.database_definition import *

# base = 'https://d3gtl9l2a4fn1j.cloudfront.net/t/p/w'
        # self.poster = QWebView()
        # self.poster.load(QUrl(base + str(size) + movie.poster))
        # self.poster.setFixedSize(92, 138)


def info_message(parent, message):
    q = QMessageBox(parent)
    q.setText(message)
    q.setWindowTitle('Info Message')
    q.show()


class Download(QPushButton):

    def __init__(self, p, download=None):
        super(Download, self).__init__()

        self.packet = p
        self.movie = p.movie
        self.download_object = download
        self.episode = p.episode

        if self.movie is None:
            self.movie = self.episode.title
            self.title = self.movie.title + ' S' + number_format(self.episode.season) + ' E' + number_format(self.episode.episode)
        else:
            self.title = self.movie.title

        self.pause_button = QPushButton(QIcon('img/pause.png'), '')
        self.pause_button.setToolTip('Pause Download')
        self.stop_button = QPushButton(QIcon('img/stop.png'), '')
        self.stop_button.setToolTip('Stop Download')
        self.restart_button = QPushButton(QIcon('img/repeat.png'), '')
        self.restart_button.setToolTip('Restart Download')

        title = QLabel(self.title)
        title.setAlignment(Qt.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setValue(0)

        self.time = QTimeEdit()
        self.time.setReadOnly(True)

        self.time.setTime(QTime(10, 00, 0))
        self.speed = QDoubleSpinBox()
        self.speed.setSuffix(' ko/s')
        self.speed.setReadOnly(True)
        self.speed.setRange(0, 100000)

        self.layout = QGridLayout()
        self.layout.addWidget(title,             0, 0, 1, 10)
        self.layout.addWidget(self.progress,     0, 10, 1, 32)

        self.layout.addWidget(self.pause_button,   0, 42, 1, 1)
        self.layout.addWidget(self.stop_button,    0, 43, 1, 1)
        self.layout.addWidget(self.restart_button, 0, 44, 1, 1)

        q = QLabel('ETA')
        q.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(q,                 1, 0, 1, 10)
        self.layout.addWidget(self.time,         1, 10, 1, 10)

        q = QLabel('Speed')
        q.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(q,                 1, 30, 1, 10)
        self.layout.addWidget(self.speed,        1, 40, 1, 5)
        self.setLayout(self.layout)

        # Index in parent Widget
        self.index = 0
        self._parent = None

    def remove_from_parent(self):
        if self._parent is not None:
            self._parent.remove_download(self.index)

    def set_enabled(self, v):
        self.setEnabled(v)

        if v is True:
            self.setStyleSheet('background-color:rgb(33,33,3)')
        else:
            self.setStyleSheet('background-color:rgb(44,44,44)')

    def update_data(self):
        self.progress.setValue(self.download_object.progress() * 100)
        self.set_eta(self.download_object.eta(1))
        self.set_speed(self.download_object.instant_speed())

    def set_button_action(self, pause=None, stop=None, restart=None):
        # lambda: info_message(self, 'Not Implemented')
        if pause is not None:
            self.connect(self.pause_button, SIGNAL('clicked()'), pause)
        if stop is not None:
            self.connect(self.stop_button, SIGNAL('clicked()'), stop)
        if restart is not None:
            self.connect(self.restart_button, SIGNAL('clicked()'), restart)

    def set_eta(self, second):
        h = second // 3600
        m = (second % 3600) // 60
        s = (second % 3600) % 60
        self.time.setTime(QTime(h, m, s))

    def set_speed(self, s):
        self.speed.setValue(s)

    def set_progress(self, p):
        self.progress.setValue(p)

    def sizeHint(self):
        # Take into account QScrollBar Size
        # s = self.layout.sizeHint()
        return self.layout.sizeHint()   # QSize(s.width() - 20, s.height())


class Manager(QScrollArea):
    """ Download Manager Class """

    def __init__(self):
        super(Manager, self).__init__()

        self.container = QWidget()
        self._layout = QVBoxLayout()
        self.container.setLayout(self._layout)
        self.setWidget(self.container)
        self.widget_array = []
        self.setAlignment(Qt.AlignCenter)
        self.shift = 0

    def _reload_download(self, widget):
        # Hardcore reloading
        # temporary so C++ Objects will not be deleted

        w = QWidget()
        l = QVBoxLayout()
        w.setLayout(l)
        self.widget_array = []

        for i in widget:
            self.widget_array.append(i)
            l.addWidget(i)

        self.setWidget(self.container)
        self.container = w
        self.layout = l
        self.setWidget(w)

        self.container.setFixedHeight(self.layout.sizeHint().height())
        self.container.setMinimumWidth(self.layout.sizeHint().width())
        self.container.resize(self.size())

    def add_download(self, m):
        d = Download(m)
        d._parent = self
        self.widget_array.append(d)
        self._layout.addWidget(d)

        self.container.setFixedHeight(self._layout.sizeHint().height())
        self.container.setMinimumWidth(self._layout.sizeHint().width())
        self.container.resize(self.size())
        return d

    def remove_download(self, idx):
        del self.widget_array[idx]
        self._reload_download(self.widget_array)

        n = len(self.widget_array)

        # update children Index
        if idx < n:
            for i in range(idx, n):
                self.widget_array[i].index = i

    def get_download(self, idx):
        return self.widget_array[idx]


if __name__ == '__main__':

    import sys
    from GUI.style import set_style

    QApplication.setStyle(QStyleFactory.create('Plastique'))
    app = QApplication(sys.argv)

    #
    db = 'C:/ZenBBData/my_db.db'
    engine = create_engine('sqlite:///' + db, echo=False)
    db = create_db(engine)

    m = db.query(XDCCPackage).limit(5).all()

    set_style(app)

    main = Manager()
    d = None
    for i in m:
        d = main.add_download(i)

    d.remove_from_parent()
    main.show()

    sys.exit(app.exec_())