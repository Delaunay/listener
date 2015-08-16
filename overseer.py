# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from GUI.zenbb import *
from XDCC.multibot import *
from GUI.style import set_style
import sys


class Overseer():
    """ Multibot + ZenBB"""

    def __init__(self):

        db = 'C:/ZenBBData/my_db.db'
        self.engine = create_engine('sqlite:///' + db, echo=False)
        self.db = create_db(self.engine)

        # connection = self.s.query(XDCCServer).filter(XDCCServer.url == 'irc.criten.net').limit(1).all()
        connection = self.db.query(XDCCServer).all()
        cb = CallBack()
        cb.info.policy = 1

        self.bot = MultiBot(connection)

        # self.bot.callback = lambda p, y: cb.add_packet(p, self.db, y)
        self.bot.irc.download_end_callback = self.download_end
        self.bot.irc.download_starting_callback = self.download_start
        self.bot.irc.download_progress_callback = self.download_progress

        self.gui = None

    def download_start(self, dcc_connection, info):
        # Add GUI Download
        d = self.gui.widget_manager.add_download(info)
        dcc_connection.user_defined = d

    @staticmethod
    def download_progress(dcc_connection, info):
        d = dcc_connection.user_defined
        d.set_speed(dcc_connection.average_speed())
        d.set_eta(dcc_connection.eta(1))
        d.set_progress(100 * dcc_connection.completed())

    @staticmethod
    def download_end(dcc_connection, info):
        dcc_connection.user_defined.remove_from_parent()

    def download_action(self, packet, msg):

        #print(packet.server, packet.pkg, packet.bot)
        # gui_item = self.gui.widget_manager.add_download(packet)
        self.bot.irc.request_dcc_packet(packet.server, packet.bot, packet.pkg, info=packet, channel=packet.channel)

    def start(self):
        QApplication.setStyle(QStyleFactory.create('Plastique'))
        app = QApplication(sys.argv)
        set_style(app)

        self.gui = ZenBB(self.db)
        self.gui.download_action = self.download_action
        self.gui.start()

        # Custom loop
        try:
            while self.gui.running:
                app.processEvents()
                self.bot.irc.reactor.process_once()
        finally:
            self.db.commit()

a = Overseer()
a.start()