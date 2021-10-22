# -*- coding: utf-8 -*-
import ctypes
import sys

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication
from at.gui.utils import get_dpi
from atktima.gui.ktima import KtimaUI
from atktima.settings import *

if __name__ == "__main__":

    myappid = 'com.aztool.atktima.app'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    if get_dpi() < 120:
        SEGOE = QFont(FONT, FONTSIZE)
    else:
        SEGOE = QFont(FONT, FONTSIZE - 2)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APPICON))
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = KtimaUI(size=(None, 600))
    ui.show()

    sys.exit(app.exec_())
