# -*- coding: utf-8 -*-
__author__ = 'Pierre Delaunay'

from PyQt4.Qt import *


def set_style(app):
    """ Define Qt Dark Style"""

    font = QFont("Op/enSans-Regular.svg")

    p = app.palette()
    p.setColor(QPalette.Window,		QColor(53, 53, 53))
    p.setColor(QPalette.WindowText,	QColor(255, 255, 255))
    p.setColor(QPalette.Base,		QColor(5, 5, 5))
    p.setColor(QPalette.Text,		QColor(255, 255, 255))
    p.setColor(QPalette.Button,		QColor(33, 33, 33))
    p.setColor(QPalette.ButtonText,	QColor(255, 255, 255))
    p.setColor(QPalette.Highlight,	QColor(100, 100, 200))
    p.setColor(QPalette.BrightText,	QColor(255, 255, 255))
    p.setColor(QPalette.Midlight,	QColor(55, 55, 55))
    p.setColor(QPalette.Dark,		QColor(55, 55, 55))
    p.setColor(QPalette.Mid,		QColor(55, 55, 55))
    p.setColor(QPalette.Shadow,		QColor(55, 55, 55))
    app.setPalette(p)
    # app.setFont(font)