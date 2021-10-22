# -*- coding: utf-8 -*-
from os import path
import sys
from pathlib import Path
from time import sleep
from typing import Any, Tuple, Union
import pandas as pd
from atktima.utils.anartisi import anartisi
from at.auth.utils import load_lic
from at.gui.line import HLine
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
from at.result import Result
from at.path import PathEngine
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from atktima.path import paths
from atktima.state import state
from atktima.sql import db

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class AnartisiTab(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)
        self.pickedMeleti = state['meleti']
        self.threadpool = QThreadPool(parent=self)
        self.popup = Popup(state['appname'])
        self.mapping.lineEdit.textChanged.connect(self.clearCombos)
        self.buttonAnartisi.subscribe(self.onAnartisi)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        labelLayout = QHBoxLayout()

        self.fullname = Label(icon='person-fill',
                              label=state['fullname'],
                              parent=self)
        self.username = Label(icon='person-badge-fill',
                              label=state['username'],
                              parent=self)
        self.company = Label(icon='house-fill',
                             label=state['company'],
                             parent=self)
        self.meleti = Label(icon='layers-fill',
                            label=state['meleti'],
                            parent=self)

        self.apospasmata = FolderInput(label="Φάκελος με αποσπάσματα",
                                       orientation=VERTICAL,
                                       parent=self)
        self.organized = FolderInput(label="Φάκελος που θα οργανωθούν τα αποσπάσματα",
                                     orientation=VERTICAL,
                                     parent=self)
        self.mapping = FileInput(label="Αρχείο excel με αντιστοιχίσεις",
                                 orientation=VERTICAL,
                                       parent=self)
        self.mapping.setBrowseCallback(self.getExcelCols)

        self.filename = ComboInput("Στήλη ονόματος αρχείου",
                                   labelsize=(150, 24),
                                   combosize=(200, 24),
                                   parent=self)
        self.region = ComboInput("Στήλη περιοχής",
                                 labelsize=(150, 24),
                                 combosize=(200, 24),
                                 parent=self)
        self.page = ComboInput("Στήλη σελίδων",
                               labelsize=(150, 24),
                               combosize=(200, 24),
                               parent=self)
        self.tk = ComboInput("Στήλη ΤΚ",
                             labelsize=(150, 24),
                             combosize=(200, 24),
                             parent=self)
        self.progress = ProgressBar(parent=self)
        self.status = StatusButton(parent=self)
        self.buttonAnartisi = Button(label="Οργάνωση αποσπασμάτων",
                                     size=(180, 30),
                                     parent=self)

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.apospasmata)
        layout.addWidget(self.mapping)
        layout.addWidget(HLine())
        layout.addWidget(self.filename)
        layout.addWidget(self.region)
        layout.addWidget(self.page)
        layout.addWidget(self.tk)
        layout.addWidget(HLine())
        layout.addWidget(self.organized)
        layout.addWidget(HLine())
        layout.addWidget(self.buttonAnartisi, stretch=2,
                         alignment=Qt.AlignCenter)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)

        self.setLayout(layout)

    def getExcelCols(self):
        _file = self.mapping.getText()
        if _file:
            file_path = Path(_file)
            if file_path.exists():
                _file_ext = file_path.suffix
                if _file_ext in ['.xlsx', '.xls']:
                    _df = pd.read_excel(_file)
                    _cols = _df.columns.tolist()

                    self.filename.addItems(_cols)
                    self.region.addItems(_cols)
                    self.page.addItems(_cols)
                    self.tk.addItems(_cols)

    def clearCombos(self):
        self.filename.clearItems()
        self.region.clearItems()
        self.page.clearItems()
        self.tk.clearItems()

    def updateProgress(self, metadata: dict):
        if metadata:
            progress_now = metadata.get('pbar', None)
            progress_max = metadata.get('pbar_max', None)
            status = metadata.get('status', None)

            if progress_now is not None:
                self.progress.setValue(progress_now)
            if progress_max is not None:
                self.progress.setMaximum(progress_max)
            if status is not None:
                self.status.disable(str(status))

    def updateResult(self, status: Any):
        if status is not None:
            if isinstance(status, AuthStatus):
                if not status.authorised:
                    self.popup.error(status.msg)
            elif isinstance(status, Result):
                if status.result == Result.ERROR:
                    self.popup.error(status.msg)
                elif status.result == Result.WARNING:
                    self.popup.warning(status.msg, **status.details)
                else:
                    self.popup.info(status.msg, **status.details)
            else:
                self.popup.info(status)

    def updateFinish(self):
        pass

    def onAnartisi(self):
        run_thread(threadpool=self.threadpool,
                   function=self.makeAnartisi,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    @licensed(appname=state['appname'], category=state['meleti'])
    def makeAnartisi(self, _progress):
        src = self.apospasmata.getText()
        dst = self.organized.getText()
        mapping_file = self.mapping.getText()

        col_filename = self.filename.getCurrentText()
        col_region = self.region.getCurrentText()
        col_page = self.page.getCurrentText()
        col_tk = self.tk.getCurrentText()

        if all([bool(src),
                bool(dst),
                bool(mapping_file),
                bool(col_filename),
                bool(col_region),
                bool(col_page),
                bool(col_tk)]):
            return anartisi(src=src,
                            dst=dst,
                            mapping_file=mapping_file,
                            col_filename=col_filename,
                            col_region=col_region,
                            col_page=col_page,
                            col_tk=col_tk,
                            _progress=_progress)
        else:
            return Result.error("Κάποια από τις κατηγορίες δεν είναι συμπληρωμένη")


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = AnartisiTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
