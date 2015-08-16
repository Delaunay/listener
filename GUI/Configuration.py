# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from PyQt4.Qt import *
from Database.database_definition import *
from copy import deepcopy
from collections import OrderedDict, ChainMap


Options = ChainMap({
    'XDCC': {
        'Passive Database Building': {'Value': True, 'Type': 'CheckBox'},
        'Active Database Building': {'Value': False, 'Type': 'CheckBox'},
    },
    'Torrent': {
        'Search Torrent':  {'Value': False, 'Type': 'CheckBox'},
        'Use All': {'Value': False, 'Type': 'CheckBox'},
    },
    'Direct Download': {
        'Use Direct Download': {'Value': False, 'Type': 'CheckBox'},
    },
    'Data Sharing': {
        'Enabled': {'Value': False, 'Type': 'CheckBox'},
    },

    'Adult': {
        'Enabled': {'Value': False, 'Type': 'CheckBox'},
    },

    'Metadata Lookup': {
        'Enabled': {'Value': False, 'Type': 'CheckBox'},
        'Lookup Service': {'Value': 'tmdb', 'Type': 'ComboBox', 'Choice': ['tmdb']},
        'Adult Lookup Service': {'Value': 'CDUniverse', 'Type': 'ComboBox', 'Choice': ['CDUniverse']},
    },

    'Track TV': {
        'Enabled': {'Value': False, 'Type': 'CheckBox'},
        'Username': {'Value': '', 'Type': 'LineEdit'},
        'Password': {'Value': '', 'Type': 'LineEdit'}
    },

    'Download Planner': {
        'Enabled': {'Value': False, 'Type': 'CheckBox'},
        'Size Movie': {'Value': '663 MB', 'Type': 'LineEdit'},
        'Size TV': {'Value': '663 MB', 'Type': 'LineEdit'},
        'Quality Movie': {'Value': '720p', 'Type': 'LineEdit'},
        'Quality TV': {'Value': '720p', 'Type': 'LineEdit'},
    },

    'Security': {
        'Require SSL': {'Value': False, 'Type': 'CheckBox'},
    }
})


class Configuration(QScrollArea):

    def __init__(self, options=deepcopy(Options)):
        super(Configuration, self).__init__()

        self.container = QWidget()
        self.layout = QGridLayout()
        # self.layout.setAlignment(Qt.AlignCenter)
        self.container.setLayout(self.layout)
        self.setWidget(self.container)
        self.setAlignment(Qt.AlignCenter)

        img = QWebView()
        img.load(QUrl('google.com'))
        img.setFixedSize(342, 513)

        self.row = 0

        for i in options:
            self.add_title(i)

            for j in options[i]:
                self.add_option(j, options[i][j])

        self.layout.addWidget(img, 0, 11, self.row, 10)
        self.container.resize(self.layout.sizeHint())

    def add_title(self, title):

        self.layout.addWidget(QLabel(title), self.row, 0, 1, 10)
        self.container.resize(self.layout.sizeHint())
        self.row += 1

    def add_option(self, label, info):
        l = QLabel(label)
        l.setAlignment(Qt.AlignRight)
        self.layout.addWidget(l, self.row, 1, 1, 5)
        self.add_widget(info)
        self.row += 1
        self.container.resize(self.layout.sizeHint())

    def add_widget(self, info):

        b = None
        if info['Type'] == 'CheckBox':
            b = QCheckBox()
            if info['Value']:
                b.setCheckState(Qt.Checked)

        if info['Type'] == 'LineEdit':
            b = QLineEdit()

            if 'Value' in info:
                b.setText(info['Value'])

        if info['Type'] == 'ComboBox':
            b = QComboBox()

            for k in info['Choice']:
                b.addItem(k)

        if b is not None:
            self.layout.addWidget(b, self.row, 6, 1, 5)

    def save_config(self):
        pass

    def load_config(self):
        pass


if __name__ == '__main__':

    import sys
    from GUI.style import set_style

    QApplication.setStyle(QStyleFactory.create('Plastique'))
    app = QApplication(sys.argv)

    #
    db = 'C:/ZenBBData/my_db.db'
    engine = create_engine('sqlite:///' + db, echo=False)
    db = create_db(engine)

    m = db.query(Movie).all()[0]

    set_style(app)

    main = Configuration()
    main.show()

    sys.exit(app.exec_())