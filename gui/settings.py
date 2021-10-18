# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from time import sleep
from typing import Any, Tuple, Union

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
from at.path import PathEngine
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

from atktima.path import paths
from atktima.state import state

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class SettingsTab(QWidget):
    meletiChanged = pyqtSignal()

    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)
        self.pickedMeleti = state['meleti']
        self.threadpool = QThreadPool(parent=self)
        self.save.subscribe(self.onSave)
        self.licButton.subscribe(self.onLicUpload)
        self.meletes.subscribe(self.onMeletiChanged)
        self.kthmadata.lineEdit.textChanged.connect(self.settingsChanged)
        self.kthmatemp.lineEdit.textChanged.connect(self.settingsChanged)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        labelLayout = QHBoxLayout()
        meletiLayout = QHBoxLayout()
        licLayout = QHBoxLayout()

        self.fullname = Label(icon='person-fill',
                              label=state['fullname'],
                              parent=self)
        self.username = Label(icon='person-badge-fill',
                              label=state['username'],
                              parent=self)
        self.company = Label(icon='house-fill',
                             label=state['company'],
                             parent=self)
        self.meleti = Label(icon='info-circle-fill',
                            label=state[state['meleti']]['name'],
                            parent=self)
        self.app = Label(icon='app',
                         label=state['appname'],
                         parent=self)
        self.version = Label(icon='hash',
                             label=state['version'],
                             parent=self)
        self.kthmatemp = FolderInput(label='kthmatemp',
                                     editsize=(100, 24),
                                     parent=self)
        self.kthmadata = FolderInput(label='kthmadata',
                                     editsize=(100, 24),
                                     parent=self)
        self.meletes = ComboInput(label="Μελέτη",
                                  combosize=(100, 24),
                                  items=state['all_mel_codes'],
                                  parent=self)
        self.lic = FileInput(label="Άδεια",
                             parent=self)
        self.licButton = Button(label="Φόρτωση",
                                icon='upload',
                                size=(90, 22))
        self.save = Button("Αποθήκευση Αλλαγών",
                           size=(140, 26),
                           parent=self)
        self.status = StatusButton(parent=self)

        self.meletes.setCurrentText(state['meleti'])
        self.kthmatemp.setText(state['kthmatemp'])
        self.kthmadata.setText(state['kthmadata'])
        self.save.disable()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.app)
        labelLayout.addWidget(self.version)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        meletiLayout.addWidget(self.meletes)
        meletiLayout.addWidget(self.meleti, stretch=2, alignment=Qt.AlignLeft)
        layout.addLayout(meletiLayout)
        layout.addWidget(self.kthmatemp, alignment=(Qt.AlignLeft | Qt.AlignTop))
        layout.addWidget(self.kthmadata, alignment=(Qt.AlignLeft | Qt.AlignTop))
        layout.addWidget(self.save, alignment=Qt.AlignRight)
        layout.addWidget(HLine())
        licLayout.addWidget(self.lic)
        licLayout.addWidget(self.licButton)
        layout.addLayout(licLayout, stretch=0)
        layout.addWidget(self.status, stretch=2, alignment=Qt.AlignBottom)

        self.setLayout(layout)

    def updateProgress(self, metadata: dict):
        if metadata:
            progress_now = metadata.get('pbar', None)
            progress_max = metadata.get('pbar_max', None)
            status = metadata.get('status', None)

            if progress_now is not None:
                self.progress.setValue(progress_now)
            if progress_max is not None:
                self.progress.setValue(progress_max)
            if status is not None:
                self.status.disable(str(status))

    def updateResult(self, status: Any):
        if status is not None:
            if isinstance(status, AuthStatus):
                if not status.authorised:
                    self.pop.error(status.info)
            elif isinstance(status, str):
                self.status.enable(status)

    def updateFinish(self):
        pass

    def settingsChanged(self):
        mel_changed = self.pickedMeleti != state['meleti']
        data_changed = self.kthmadata.getText() != state['kthmadata']
        temp_changed = self.kthmatemp.getText() != state['kthmatemp']
        if data_changed or temp_changed or mel_changed:
            self.save.enable()
        else:
            self.save.disable()

    def onMeletiChanged(self):
        self.pickedMeleti = self.meletes.getCurrentText()
        self.meleti.setText(state[self.pickedMeleti]['name'])

        self.settingsChanged()
        self.status.disable()

    def onSave(self):
        run_thread(threadpool=self.threadpool,
                   function=self.saveAction,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    def onLicUpload(self):
        run_thread(threadpool=self.threadpool,
                   function=self.licUploadAction,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    def licUploadAction(self, _progress):
        src = self.lic.getText()
        load_lic(filepath=src, dst=paths.get_authfolder())
        _progress.emit({'status': "Η προσωρινή άδεια φορτώθηκε επιτυχώς"})

    def saveAction(self, _progress):
        state['meleti'] = self.pickedMeleti
        state['kthmatemp'] = self.kthmatemp.getText()
        state['kthmadata'] = self.kthmadata.getText()

        state.update_db()
        _progress.emit({'status': "Οι ρυθμίσεις αποθηκεύτηκαν"})
        self.meletiChanged.emit()


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = SettingsTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
