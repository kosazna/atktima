# -*- coding: utf-8 -*-
import ctypes
import sys

from at.gui.utils import get_dpi
from at.logger import log
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QApplication

from atktima.app.settings import *
from atktima.app.ui import KtimaUI

if __name__ == "__main__":

    appid = 'com.aztool.atktima.app'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    if get_dpi() < 120:
        SEGOE = QFont(FONT, FONTSIZE)
    else:
        SEGOE = QFont(FONT, FONTSIZE - 1)

    log.set_mode("GUI")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APPICON))
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = KtimaUI(size=(None, 650))
    ui.show()

    sys.exit(app.exec_())
