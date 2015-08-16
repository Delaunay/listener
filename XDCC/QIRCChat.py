# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from PyQt4.Qt import *
from XDCC.IRCChat import *


class QIRCChat(QMainWindow):

    def __init__(self):
        super(QIRCChat, self).__init__()

        # Qt Stuff
        #==========================================
        # Declaration

        # Server Widget
        sw = QDockWidget()
        self.server_widget = QTreeWidget()
        sw.setWidget(self.server_widget)
        self.addDockWidget(Qt.LeftDockWidgetArea, sw)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # self.layout = QGridLayout()
        # self.chat_view = QTextEdit()
        # self.chat_view.setReadOnly(True)
        # self.message_view = QLineEdit()
        # self.message_view.setPlaceholderText('Message')
        # self.running = True

        # # Layout setup
        # self.layout.addWidget(self.chat_view, 0, 0, 4, 4)
        # self.layout.addWidget(self.message_view, 4, 0, 1, 4)
        # self.setLayout(self.layout)
        #
        # # Event handling
        # self.connect(self.message_view, SIGNAL('returnPressed()'), self.send_message)

        # Dispatch Event
        self.irc_chat = IRCChat()
        self.irc_chat.reactor.add_global_handler("all_events", self._dispatcher, -10)

    def append_message(self, msg):
        self.chat_view.append(msg)
        self.chat_view.setTextColor(QColor(255, 255, 255))

    def set_text_color(self, r, g, b):
        self.chat_view.setTextColor(QColor(r, g, b))

    def send_message(self):
        self.set_text_color(140, 140, 140)
        self.append_message(self.message_view.text())
        self.message_view.setText('')

    def _dispatcher(self, connection, event):
        """ Dispatch events to on_<event.type> method, if present.  """
        do_nothing = lambda c, e: None
        method = getattr(self, "on_" + event.type, do_nothing)
        print(event.type)
        method(connection, event)

    def on_privnotice(self, c, e):
        self.chat_view.setTextColor(QColor(255, 0, 0))
        self.append_message(printable(e.arguments[0]))

    def on_welcome(self, c, e):
        self.chat_view.setTextColor(QColor(0, 255, 255))
        self.append_message(printable(e.arguments[0]))

    def on_nicknameinuse(self, c, e):
        self.chat_view.setTextColor(QColor(255, 255, 0))
        self.append_message('Nickname taken')

        self.nick += '_'
        # self.r.connect('irc.otaku-irc.fr', 6667, self.nick)

    def on_join(self, c, e):
        self.chat_view.setTextColor(QColor(255, 0, 255))
        self.append_message('Join success')

    def on_pubmsg(self, c, e):
        self.append_message(printable(e.arguments[0]))

    def on_disconnect(self, c, e):
        self.append_message('Disconnected')
        self.r.reconnect()
        # sys.exit(0)

    def on_all_raw_messages(self, c, e):
        print(printable(e.arguments[0]))


if __name__ == '__main__':

    import sys
    from GUI.style import set_style

    try:
        os.remove('test')
    except:
        pass

    QApplication.setStyle(QStyleFactory.create('Plastique'))
    app = QApplication(sys.argv)

    set_style(app)

    main = QIRCChat()
    main.show()

    # Custom App loop
    #while main.running:
    #    app.processEvents()
        # main.reactor.process_once()

    sys.exit(app.exec_())