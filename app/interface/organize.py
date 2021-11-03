# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

from at.auth.client import AuthStatus, licensed
from at.gui.components import *
from at.gui.utils import VERTICAL, set_size
from at.gui.worker import run_thread
from at.io.copyfuncs import copy_pattern_from_files
from at.logger import log
from at.result import Result
from atktima.app.settings import (ORGANIZE_FILTER, ORGANIZE_READ_SCHEMA,
                                  ORGANIZE_SAVE_SCHEMA)
from atktima.app.utils import db, paths, state
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class OrganizeTab(QWidget):
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
        self.buttonFilterTest.subscribe(self.onTestFilter)
        self.buttonPatternTest.subscribe(self.onTestPattern)
        self.buttonCopy.subscribe(self.onCopyPattern)
        self.inputFolder.subscribe(self.onInputSelectorChange)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        inputFolders = {"Ανακτήσεις": paths.get_anaktiseis_in(),
                        "Σαρωμένα": paths.get_saromena_in()}
        outputFolders = {"Ανακτήσεις": paths.get_anaktiseis_out(),
                         "Σαρωμένα": paths.get_saromena_out(),
                         "Χωρικά": paths.get_localdata()}

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 4, 2, 0)
        labelLayout = QHBoxLayout()
        inputLayout = QVBoxLayout()
        outputLayout = QVBoxLayout()
        buttonLayout = QVBoxLayout()
        buttonTestLayout = QHBoxLayout()

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
        self.inputFolder = PathSelector(label="Εύρεση σε",
                                        mapping=inputFolders,
                                        labelsize=(180, 24),
                                        orientation=VERTICAL,
                                        parent=self)
        self.inputPattern = StrSelector(label="Δομή",
                                        mapping=ORGANIZE_READ_SCHEMA,
                                        combosize=(200, 24),
                                        editsize=(300, 24),
                                        parent=self)
        self.filters = FilterFileSelector("Φίλτρα", parent=self)
        self.ouputFolder = PathSelector(label="Απόθεση σε",
                                        mapping=outputFolders,
                                        labelsize=(180, 24),
                                        orientation=VERTICAL,
                                        parent=self)
        self.outputPattern = StrSelector(label="Δομή",
                                         mapping=ORGANIZE_SAVE_SCHEMA,
                                         combosize=(200, 24),
                                         editsize=(300, 24),
                                         parent=self)
        self.outputName = StrInput(label="Με όνομα",
                                   parent=self)
        self.counter = StatusLabel(label="Πλήθος αρχείων",
                                   labelsize=(100, 24),
                                   statussize=(100, 24),
                                   parent=self)

        self.buttonCopy = Button(label='Οργνάνωση Αρχείων',
                                 color='blue',
                                 size=(200, 30),
                                 parent=self)
        self.buttonFilterTest = Button(label='Δοκιμή Φίλτρου',
                                       size=(150, 24),
                                       parent=self)
        self.buttonPatternTest = Button(label='Δοκιμή Μοτίβου',
                                        size=(150, 24),
                                        parent=self)
        self.status = StatusButton(parent=self)

        self.outputName.setPlaceholder("Προαιρετικό όνομα αποθήκευσης")
        self.filters.recursive.setText("Εύρεση σε υποφακέλους")
        self.onInputSelectorChange()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        inputLayout.addWidget(self.inputFolder)
        inputLayout.addWidget(self.filters)
        inputLayout.addWidget(self.inputPattern)
        layout.addLayout(inputLayout)
        layout.addWidget(HLine())
        outputLayout.addWidget(self.ouputFolder)
        outputLayout.addWidget(self.outputName)
        outputLayout.addWidget(self.outputPattern)
        layout.addLayout(outputLayout)
        layout.addWidget(HLine())
        buttonTestLayout.addWidget(
            self.counter, stretch=2, alignment=Qt.AlignLeft)
        buttonTestLayout.addWidget(self.buttonFilterTest)
        buttonTestLayout.addWidget(self.buttonPatternTest)
        buttonLayout.addLayout(buttonTestLayout)
        buttonLayout.addWidget(self.buttonCopy, alignment=Qt.AlignCenter)
        layout.addLayout(buttonLayout)
        layout.addWidget(self.status, stretch=2, alignment=Qt.AlignBottom)

        self.setLayout(layout)

    def onInputSelectorChange(self):
        mode = self.inputFolder.getCurrentText()

        if mode in ORGANIZE_FILTER:
            _find = ORGANIZE_FILTER[mode][0]
            _find_mode = ORGANIZE_FILTER[mode][1]
            _what = ORGANIZE_FILTER[mode][2]

            self.filters.setText(_find, _find_mode, _what)
        else:
            self.filters.setText('all', 'exact', '')

    def updateProgress(self, metadata: dict):
        if metadata:
            progress_now = metadata.get('pbar', None)
            progress_max = metadata.get('pbar_max', None)
            status = metadata.get('status', None)
            count = metadata.get('count', None)

            if progress_now is not None:
                self.progress.setValue(progress_now)
            if progress_max is not None:
                self.progress.setMaximum(progress_max)
            if status is not None:
                self.status.disable(str(status))
            if count is not None:
                self.setCount(count)

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

    def setCount(self, count: int):
        self.counter.setText(str(count))

    def validate(self, funcname: str):
        src = self.inputFolder.getText()
        filter_str = self.filters.getText()

        read_pattern = self.inputPattern.getText()
        dst = self.ouputFolder.getText()
        save_pattern = self.outputPattern.getText()

        probs = []

        if funcname == 'onTestPattern':
            if not src or not Path(src).exists():
                probs.append("-Δεν βρέθηκε φάκελος προέλευσης")
            if not filter_str:
                probs.append("-Δεν βρέθηκε φίλτρο")
            if not read_pattern:
                probs.append("-Δεν βρέθηκε δομή προέλευσης")
            if not dst or not Path(dst).exists():
                probs.append("-Δεν βρέθηκε φάκελος προορισμού")
            if not save_pattern:
                probs.append("-Δεν βρέθηκε δομή προορισμού")
        elif funcname == 'onTestFilter':
            if not src or not Path(src).exists():
                probs.append("-Δεν βρέθηκε φάκελος προέλευσης")
            if not filter_str:
                probs.append("-Δεν βρέθηκε φίλτρο")
        elif funcname == 'copyFiles':
            if not src or not Path(src).exists():
                probs.append("-Δεν βρέθηκε φάκελος προέλευσης")
            if not filter_str:
                probs.append("-Δεν βρέθηκε φίλτρο")
            if not read_pattern:
                probs.append("-Δεν βρέθηκε δομή προέλευσης")
            if not dst or not Path(dst).exists():
                probs.append("-Δεν βρέθηκε φάκελος προορισμού")
            if not save_pattern:
                probs.append("-Δεν βρέθηκε δομή προορισμού")

        if probs:
            details = '\n'.join(probs)
            return Result.warning('Προσδιόρισε όλες τις απαραίτητες παραμέτρους',
                                  details={'secondary': details})
        return None

    def onCopyPattern(self):
        return run_thread(threadpool=self.threadpool,
                          function=self.copyPattern,
                          on_update=self.updateProgress,
                          on_result=self.updateResult,
                          on_finish=self.updateFinish)

    def onTestFilter(self):
        return run_thread(threadpool=self.threadpool,
                          function=self.testFilter,
                          on_update=self.updateProgress,
                          on_result=self.updateResult,
                          on_finish=self.updateFinish)

    def onTestPattern(self):
        return run_thread(threadpool=self.threadpool,
                          function=self.testPattern,
                          on_update=self.updateProgress,
                          on_result=self.updateResult,
                          on_finish=self.updateFinish)

    @licensed(appname=state['appname'], category=state['meleti'])
    def copyPattern(self, _progress):
        validation = self.validate('copyFiles')
        if validation is not None:
            return validation

        src = self.inputFolder.getText()
        file_filter = self.filters.getFilterObject()
        filter_str = self.filters.getText()
        keep = self.filters.getKeepValue()
        files = file_filter.search(src, keep)
        nfiles = len(files)
        read_pattern = self.inputPattern.getText()
        dst = self.ouputFolder.getText()
        save_pattern = self.outputPattern.getText()
        save_name = self.outputName.getText()

        if save_pattern:
            _save_pattern = save_pattern
        else:
            _save_pattern = None

        if save_name:
            _save_name = save_name
        else:
            _save_name = None

        _progress.emit({'count': nfiles})

        if files:
            log.success(
                f"\nΑρχεία: {nfiles} | Αποτελέσματα φίλτρου: {filter_str}\n")
            return copy_pattern_from_files(files=files,
                                           dst=dst,
                                           read_pattern=read_pattern,
                                           save_pattern=_save_pattern,
                                           save_name=_save_name,
                                           verbose=True,
                                           mode='execute')
        else:
            log.error(
                f"\nΑρχεία: {nfiles} | Αποτελέσματα φίλτρου: {filter_str}\n")

    @licensed(appname=state['appname'], category=state['meleti'])
    def testFilter(self, _progress):
        validation = self.validate('onTestFilter')
        if validation is not None:
            return validation

        file_filter = self.filters.getFilterObject()
        filter_str = self.filters.getText()
        folder = self.inputFolder.getText()
        keep = self.filters.getKeepValue()
        files = file_filter.search(folder, keep)
        nfiles = len(files)

        _progress.emit({'count': nfiles})

        if files:
            log.success(
                f"\nΑρχεία: {nfiles} | Αποτελέσματα φίλτρου: {filter_str}\n")
            for f in files:
                log.info(str(f))
        else:
            log.error(
                f"\nΑρχεία: {nfiles} | Αποτελέσματα φίλτρου: {filter_str}\n")

    @licensed(appname=state['appname'], category=state['meleti'])
    def testPattern(self, _progress):
        validation = self.validate('onTestPattern')
        if validation is not None:
            return validation

        src = self.inputFolder.getText()
        file_filter = self.filters.getFilterObject()
        filter_str = self.filters.getText()
        keep = self.filters.getKeepValue()
        files = file_filter.search(src, keep)
        nfiles = len(files)
        read_pattern = self.inputPattern.getText()
        dst = self.ouputFolder.getText()
        save_pattern = self.outputPattern.getText()
        save_name = self.outputName.getText()

        if save_pattern:
            _save_pattern = save_pattern
        else:
            _save_pattern = None

        if save_name:
            _save_name = save_name
        else:
            _save_name = None

        _progress.emit({'count': nfiles})

        if files:
            log.success(
                f"\nΑρχεία: {nfiles} | Αποτελέσματα φίλτρου: {filter_str}\n")
            copy_pattern_from_files(files=files,
                                    dst=dst,
                                    read_pattern=read_pattern,
                                    save_pattern=_save_pattern,
                                    save_name=_save_name,
                                    mode='test')
        else:
            log.error(
                f"\nΑρχεία: {nfiles} | Αποτελέσματα φίλτρου: {filter_str}\n")


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = OrganizeTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
