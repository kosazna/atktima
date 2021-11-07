# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

from at.auth.client import AuthStatus, licensed
from at.gui.components import *
from at.gui.utils import HORIZONTAL, VERTICAL, set_size
from at.gui.worker import run_thread
from at.result import Result
from atktima.app.core import forest, make_folders
from atktima.app.settings import *
from atktima.app.utils import db, paths, state
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class MiscTab(QWidget):
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
        self.buttonMakeForest.subscribe(self.onMakeForest)
        self.buttonMakeFolders.subscribe(self.onMakeFolders)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 4, 2, 0)
        labelLayout = QHBoxLayout()
        patternButtonLayout = QHBoxLayout()
        listLayout = QHBoxLayout()

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
        self.claims = FileInput(label="Αρχείο excel με διεκδίκηση",
                                orientation=VERTICAL,
                                labelsize=(250, 24),
                                parent=self)
        self.active = FileInput(label="Αρχείο excel με ενεργά δασικά",
                                orientation=VERTICAL,
                                labelsize=(250, 24),
                                parent=self)
        self.buttonMakeForest = Button("Δημιουργία FOREST",
                                       size=(140, 24),
                                       parent=self)
        self.makeFolder = FolderInput(label="Προορισμός",
                                      parent=self)
        self.shape = ListWidget(label="Επιλογή Χωρικών",
                                parent=self)
        self.otas = ListWidget(label="Επιλογή ΟΤΑ",
                               parent=self)
        self.schema = StrSelector(label="Δομή Προορισμού",
                                  mapping=LOCAL_MAPPING,
                                  combosize=(100, 24),
                                  editsize=(300, 24),
                                  labelsize=(120, 24),
                                  parent=self)
        self.buttonMakeFolders = Button("Δημιουργία φακέλων",
                                        size=(140, 24),
                                        parent=self)

        self.status = StatusButton(parent=self)

        selectorsKey = state[state['meleti']]['type']
        self.shape.addItems(db.get_shapes(state['meleti'], mdb=True))
        self.otas.addItems(db.get_ota_per_meleti_company(
            state['meleti'], state['company']))
        self.schema.setCurrentText(selectorsKey)

        self.shape.hideButtons()
        self.otas.hideButtons()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.claims)
        layout.addWidget(self.active)
        layout.addWidget(self.buttonMakeForest, stretch=2,
                         alignment=Qt.AlignRight)
        layout.addWidget(HLine())
        layout.addWidget(HLine())
        layout.addWidget(self.makeFolder)
        listLayout.addWidget(self.shape)
        listLayout.addWidget(self.otas)
        layout.addLayout(listLayout)
        patternButtonLayout.addWidget(self.schema)
        patternButtonLayout.addWidget(self.buttonMakeFolders)
        layout.addLayout(patternButtonLayout)

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

    def validate(self, funcname: str):
        claims = self.claims.getText()
        active = self.active.getText()
        local_folder = self.makeFolder.getText()
        user_otas = self.otas.getCheckState()
        local_structure = self.schema.getText()

        probs = []

        if funcname == 'makeForest':
            if not claims or not Path(claims).exists():
                probs.append("-Δεν βρέθηκε αρχείο excel διεκδίκησης")
            if not active or not Path(active).exists():
                probs.append("-Δεν βρέθηκε αρχείο excel ενεργών δασικών")
        elif funcname == 'makeFolders':
            if not local_folder or not Path(local_folder).exists():
                probs.append("-Δεν βρέθηκε ο φάκελος προορισμού")
            if not local_structure:
                probs.append("-Δεν βρέθηκε δομή προορισμού")
            if not user_otas:
                probs.append("-Δεν βρέθηκε επιλογή ΟΤΑ")

        if probs:
            details = '\n'.join(probs)
            return Result.warning('Προσδιόρισε όλες τις απαραίτητες παραμέτρους',
                                  details={'secondary': details})
        return None

    def onMakeForest(self):
        return run_thread(threadpool=self.threadpool,
                          function=self.makeForest,
                          on_update=self.updateProgress,
                          on_result=self.updateResult,
                          on_finish=self.updateFinish)

    def onMakeFolders(self):
        return run_thread(threadpool=self.threadpool,
                          function=self.makeFolders,
                          on_update=self.updateProgress,
                          on_result=self.updateResult,
                          on_finish=self.updateFinish)

    @licensed(appname=state['appname'], category=state['meleti'])
    def makeForest(self, _progress):
        validation = self.validate('makeForest')
        if validation is not None:
            return validation

        claims = self.claims.getText()
        active = self.active.getText()
        output = paths.get_databases(True).joinpath('FOREST.xlsx')

        if not paths.get_databases(True).exists():
            return Result.error(f"Δεν υπάρχει φάκελος μελέτης {state['meleti']}")

        return forest(claims=claims,
                      active_forest=active,
                      output=output,
                      _progress=_progress)

    @licensed(appname=state['appname'], category=state['meleti'])
    def makeFolders(self, _progress):
        validation = self.validate('makeFolders')
        if validation is not None:
            return validation

        local_folder = self.makeFolder.getText()
        user_shapes = self.shape.getCheckState()
        user_otas = self.otas.getCheckState()
        local_structure = self.schema.getText()

        return make_folders(dst=local_folder,
                            otas=user_otas,
                            shapes=user_shapes,
                            dst_schema=local_structure,
                            _progress=_progress)


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = MiscTab(size=(None, 600))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
