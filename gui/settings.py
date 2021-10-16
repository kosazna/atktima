# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from time import sleep
from typing import Any, Tuple, Union

from PyQt5 import QtWidgets

from at.auth.client import Authorize, AuthStatus, licensed
from at.gui.button import Button
from at.gui.check import CheckInput
from at.gui.combo import ComboInput
from at.gui.console import Console
from at.gui.filename import FileNameInput
from at.gui.icons import *
from at.gui.input import IntInput, StrInput
from at.gui.io import FileInput, FileOutput, FolderInput
from at.gui.label import Label
from at.gui.list import ListWidget
from at.gui.popup import Popup, show_popup
from at.gui.progress import ProgressBar
from at.gui.status import StatusButton, StatusLabel
from at.gui.utils import *
from at.gui.worker import run_thread
from at.io.copyfuncs import batch_copy_file, copy_file
from at.logger import log
from at.path import PathEngine
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from atktima.path import paths
from atktima.settings import

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout

cssGuide = paths.get_static(obj=True).joinpath("_style.css").read_text()

log.set_mode("GUI")
APPNAME = 'ktima'
paths = PathEngine(APPNAME)
authenticator = Authorize(APPNAME, paths.get_authfolder())


class Settings(QWidget):
    def __init__(self, parent: Optional['QWidget'] = ..., flags: typing.Union[QtCore.Qt.WindowFlags, QtCore.Qt.WindowType] = ...) -> None:
        super().__init__(parent=parent, flags=flags)