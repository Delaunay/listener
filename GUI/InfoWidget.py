# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from PyQt4.Qt import *
from Database.database_definition import *


def get_time(minute):

    h = minute // 60
    m = minute % 60

    if m < 10:
        return str(h) + ' h 0' + str(m)

    return str(h) + ' h ' + str(m)


# 500x750
# 342x513
# 154x231

# {'backdrop_sizes': ['w300', 'w780', 'w1280', 'original'],
#  'base_url': 'http://d3gtl9l2a4fn1j.cloudfront.net/t/p/',
#  'logo_sizes': ['w45', 'w92', 'w154', 'w185', 'w300', 'w500', 'original'],
#  'poster_sizes': ['w92', 'w154', 'w185', 'w342', 'w500', 'original'],
#  'profile_sizes': ['w45', 'w185', 'h632', 'original'],
#  'secure_base_url': 'https://d3gtl9l2a4fn1j.cloudfront.net/t/p/'}}

class InfoWidget(QWidget):

    def __init__(self, movie, size=342, db=None):
        super(InfoWidget, self).__init__()

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignLeft)
        base = 'http://image.tmdb.org/t/p/w'
        self.db = db
        self.packet_array = []
        # base = 'https://d3gtl9l2a4fn1j.cloudfront.net/t/p/'

        poster = QWebView()

        if movie.poster is not None:
            poster.load(QUrl(base + str(size) + movie.poster))
        else:
            poster.load(QUrl('img/default.jpg'))

        poster.setFixedSize(size, 513)
        poster_wrapper = poster

        note = QProgressBar()
        note.setRange(0, 1000)
        if movie.vote is not None:
            note.setValue(int(movie.vote * 100))
        note.setFormat('%p')

        popularity = QProgressBar()
        popularity.setRange(0, 10000)
        if movie.popularity is not None:
            popularity.setValue(int(movie.popularity * 100))
        popularity.setFormat('%p')

        overview = QTextEdit()
        if movie.overview is not None:
            overview.setText(movie.overview)
        overview.setEnabled(False)

        self.setLayout(layout)

        title_font = QFont()
        title_font.setPointSize(24)

        # Header
        title = QLabel(movie.title)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)

        if movie.type == FileType.TV:
            self.packet = self.get_packet_tv(movie)
        else:
            self.packet = self.get_packet_movie(movie)

        self.packet_info_widget = QStackedWidget()
        self.packet.setContextMenuPolicy(Qt.ActionsContextMenu)

        layout.addWidget(title,  0, 0, 1, 12)
        layout.addWidget(poster_wrapper, 2, 0, 4, 4)
        l = QLabel('Vote')
        layout.addWidget(l,     2, 4, 1, 1)
        layout.addWidget(note,  2, 5, 1, 3)
        l = QLabel('Popularity')
        layout.addWidget(l, 3, 4, 1, 1)
        layout.addWidget(popularity, 3, 5, 1, 3)
        layout.addWidget(overview, 5, 4, 1, 4)
        layout.addWidget(self.packet,             2, 8, 4, 4)
        layout.addWidget(self.packet_info_widget, 6, 4, 2, 8)

        # Download Action
        self.download = QPushButton('Downdload')
        layout.addWidget(self.download, 8, 0, 1, 12)
        self.download.connect(self.download, SIGNAL('clicked()'), self.download_action)
        self.download_action_callback = lambda x, msg: print(x, msg)

        # Copy Current Selection
        copy_action = QAction('Copy', self.packet)
        copy_action.setShortcut(Qt.CTRL + Qt.Key_C)
        clipboard = QApplication.clipboard()
        self.connect(copy_action, SIGNAL('triggered()'), lambda: clipboard.setText(self.packet.currentItem().text(1)))
        self.packet.addAction(copy_action)

        # Show Packet info
        self.packet.connect(self.packet, SIGNAL('itemSelectionChanged()'), self.show_packet_info)

        # www.imdb.com/title/ + tt0137523
        # www.imdb.com/title/tt0137523

        # print(self.sizeHint())
        layout.setAlignment(Qt.AlignCenter)

    def get_xdcc_packet(self):
        return self.packet_array[int(self.packet.currentItem().text(2))]

    def download_action(self):

        item = self.packet.currentItem()

        if item is None:
            m = QMessageBox(self)
            m.setWindowTitle('No packet were selected')
            m.setText('You have to select a packet to download')
            m.show()
            return

        txt = item.text(1)

        if txt.find(' xdcc send ') <= -1:
            m = QMessageBox(self)
            m.setWindowTitle('Incorrect Packet')
            m.setText('You have not selected a Packet')
            m.show()
            return

        # Copy to Clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(txt)

        packet = self.get_xdcc_packet()
        self.download_action_callback(packet, txt)

    def show_packet_info(self):

        item = self.packet.currentItem()

        if item is None:
            return

        txt = item.text(1)

        if txt.find(' xdcc send ') <= -1:
            return

        if self.packet_info_widget.count() > 0:
            self.packet_info_widget.removeWidget(self.packet_info_widget.widget(0))

        self.packet_info_widget.addWidget(PacketInfo(self.packet_array[int(self.packet.currentItem().text(2))]))

    def get_packet_movie(self, movie):

        ## Group Packet into server
        p = movie.xdcc_packet

        packet = QTreeWidget()
        packet.setHeaderLabel('Packets')
        k = 0

        for i in p:

            leaf = QTreeWidgetItem()
            leaf.setText(0, i.size + ' ' * 5 + i.info.replace('.', ' '))
            leaf.setText(1, '/msg ' + i.bot + ' xdcc send ' + str(i.pkg))
            leaf.setText(2, str(len(self.packet_array)))
            leaf.setText(3, str(k))
            self.packet_array.append(i)
            # self.packet_array[str(k)] = i

            packet.addTopLevelItem(leaf)
            leaf.setExpanded(True)
            k += 1

        return packet

    def get_packet_tv(self, movie):


        # Request
        episodes = self.db.query(TVShowEpisode).filter(TVShowEpisode.title_id == movie.id)\
                                          .order_by(TVShowEpisode.season)\
                                          .order_by(TVShowEpisode.episode).all()

        tree_view = QTreeWidget()
        tree_view.setHeaderLabel('Episodes')
        branch = None
        branch_season = None

        j = 0
        for i in episodes:

            if branch is None:
                branch = QTreeWidgetItem()
                branch.setText(0, 'Season ' + str(i.season))
                branch_season = i.season
                tree_view.addTopLevelItem(branch)

            if i.season == branch_season:

                episode_branch = QTreeWidgetItem()
                episode_branch.setText(0, 'Episode ' + str(i.episode))
                branch.addChild(episode_branch)

                # Order
                l = 0
                for k in i.xdcc_packet:
                    leaf = QTreeWidgetItem()
                    leaf.setText(0, k.size + ' ' * 5 + k.info.replace('.', ' '))
                    leaf.setText(1, '/msg ' + k.bot + ' xdcc send ' + str(k.pkg))
                    leaf.setText(2, str(len(self.packet_array)))
                    self.packet_array.append(k)
                    episode_branch.addChild(leaf)

                    l += 1
                j += 1
                branch.setExpanded(True)
            else:
                branch = None

        return tree_view


class PacketInfo(QWidget):

    def __init__(self, xdcc_packet):
        super(PacketInfo, self).__init__()

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel('Packet Name: '), 0, 0, 1, 1)
        layout.addWidget(QLabel('Size: '),        1, 0, 1, 1)
        layout.addWidget(QLabel('Server: '),      2, 0, 1, 1)
        # layout.addWidget(QLabel('Channel: '),     3, 0, 1, 1)
        # layout.addWidget(QPushButton('Download'), 4, 0, 1, 2)

        q = QLineEdit(xdcc_packet.original_title)
        q.setReadOnly(True)
        layout.addWidget(q, 0, 1, 1, 2)

        q = QLineEdit(xdcc_packet.size)
        q.setReadOnly(True)
        layout.addWidget(q, 1, 1, 1, 2)

        q = QLineEdit(xdcc_packet.server)
        q.setReadOnly(True)
        layout.addWidget(q, 2, 1, 1, 1)

        q = QLineEdit(xdcc_packet.channel)
        q.setReadOnly(True)
        layout.addWidget(q, 2, 2, 1, 1)


