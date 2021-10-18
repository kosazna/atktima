# -*- coding: utf-8 -*-
import ctypes
import sys

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from atktima.gui.ktima import KtimaUI
from atktima.settings import *

if __name__ == "__main__":

    myappid = 'com.aztool.atktima.app'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    SEGOE = QFont(FONT, FONTSIZE)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APPICON))
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = KtimaUI(size=(None, 600))
    ui.show()

    sys.exit(app.exec_())
