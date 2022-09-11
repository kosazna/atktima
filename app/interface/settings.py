# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from typing import Any, Optional, Tuple

from at.auth.client import AuthStatus, licensed
from at.auth.utils import load_lic
from at.gui.components import *
from at.gui.utils import set_size
from at.gui.worker import run_thread
from at.logger import log
from at.result import Result
from at.io.utils import load_json, write_json
from atktima.app.utils import db, paths, state, auth
from atktima.app.core import create_mel_folder
from atktima.app.settings import ALL_MELETES
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class SettingsTab(QWidget):
    settingsChanged = pyqtSignal()
    serverStatusChanged = pyqtSignal(tuple)

    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)
        self.pickedMeleti = state['meleti']
        self.threadpool = QThreadPool(parent=self)
        self.popup = Popup()

        self.saveButton.subscribe(self.onSave)
        self.dbButton.subscribe(lambda: db.open_db(paths.get_db_exe()))
        self.licButton.subscribe(self.onLicUpload)
        self.createButton.subscribe(self.onCreateMeleti)
        self.meletes.subscribe(self.onMeletiChanged)
        self.createMeletes.subscribe(self.onCreateMeletiChanged)

        self.kthmadata.lineEdit.textChanged.connect(self.areSettingsChanged)
        self.kthmatemp.lineEdit.textChanged.connect(self.areSettingsChanged)
        self.fullnameInsert.lineEdit.textChanged.connect(
            self.areSettingsChanged)
        self.companyInsert.lineEdit.textChanged.connect(self.areSettingsChanged)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 4, 2, 0)
        labelLayout = QHBoxLayout()
        meletiLayout = QHBoxLayout()
        datalayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()
        templayout = QHBoxLayout()
        licLayout = QHBoxLayout()
        createLayout = QHBoxLayout()

        self.fullname = Label(icon='person-fill',
                              label=state['fullname'],
                              parent=self)
        self.username = Label(icon='person-badge-fill',
                              label=state['username'],
                              parent=self)
        self.company = Label(icon='house-fill',
                             label=state['company'],
                             parent=self)
        self.meleti = Label(icon='info-square-fill',
                            label=state[state['meleti']]['name'],
                            parent=self)
        self.app = Label(icon='app',
                         label=state['appname'],
                         parent=self)
        self.version = Label(icon='hash',
                             label=state['version'],
                             parent=self)

        self.fullnameInsert = StrInput(label="Χρήστης",
                                       editsize=(250, 24),
                                       parent=self)
        self.companyInsert = StrInput(label="Εταιρία",
                                      editsize=(250, 24),
                                      parent=self)
        self.kthmatemp = FolderInput(label='kthmatemp',
                                     editsize=(250, 24),
                                     parent=self)
        self.kthmatempStatus = StatusLabel(icon='hdd-network-fill',
                                           statussize=(110, 24),
                                           parent=self)
        self.kthmadata = FolderInput(label='kthmadata',
                                     editsize=(250, 24),
                                     parent=self)
        self.kthmadataStatus = StatusLabel(icon='hdd-network-fill',
                                           statussize=(110, 24),
                                           parent=self)
        self.meletes = ComboInput(label="Μελέτη",
                                  combosize=(100, 24),
                                  items=auth.get_categories() or ALL_MELETES,
                                  parent=self)
        self.lic = FileInput(label="Άδεια",
                             parent=self)
        self.licButton = Button(label="Φόρτωση",
                                icon='upload',
                                size=(90, 22))
        self.saveButton = Button(label="Αποθήκευση Αλλαγών",
                                 size=(140, 26),
                                 parent=self)
        self.dbButton = Button(label="Άνοιγμα Βάσης",
                               icon='server',
                               size=(120, 26),
                               parent=self)
        self.createMeletes = ComboInput(label="Φάκελος μελέτης",
                                        labelsize=(120, 24),
                                        combosize=(100, 24),
                                        items=auth.get_categories(),
                                        parent=self)
        self.createButton = Button(label="Δημιουργία φακέλου",
                                   size=(140, 26),
                                   parent=self)
        self.folderStatus = StatusLabel(icon='hdd-network-fill',
                                        statussize=(110, 24),
                                        parent=self)

        self.status = StatusButton(parent=self)

        self.meletes.setCurrentText(state['meleti'])
        self.createMeletes.setCurrentText(state['meleti'])
        self.kthmatemp.setText(state['kthmatemp'])
        self.kthmadata.setText(state['kthmadata'])
        self.fullnameInsert.setText(state['fullname'])
        self.companyInsert.setText(state['company'])
        self.saveButton.disable()
        self.onCreateMeletiChanged()
        self.checkServer()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.app)
        labelLayout.addWidget(self.version)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.fullnameInsert, alignment=Qt.AlignLeft)
        layout.addWidget(self.companyInsert, alignment=Qt.AlignLeft)
        meletiLayout.addWidget(self.meletes)
        meletiLayout.addWidget(self.meleti, stretch=2, alignment=Qt.AlignLeft)

        templayout.addWidget(self.kthmatemp)
        templayout.addWidget(self.kthmatempStatus,
                             stretch=2, alignment=Qt.AlignLeft)
        datalayout.addWidget(self.kthmadata)
        datalayout.addWidget(self.kthmadataStatus,
                             stretch=2, alignment=Qt.AlignLeft)
        layout.addLayout(templayout)
        layout.addLayout(datalayout)
        layout.addLayout(meletiLayout)

        buttonLayout.addWidget(self.saveButton, alignment=Qt.AlignRight)
        buttonLayout.addWidget(self.dbButton)
        layout.addLayout(buttonLayout)
        layout.addWidget(HLine())
        createLayout.addWidget(self.createMeletes)
        createLayout.addWidget(
            self.folderStatus, stretch=2, alignment=Qt.AlignLeft)
        createLayout.addWidget(self.createButton)
        layout.addLayout(createLayout)
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

    def checkServer(self):
        if Path(self.kthmatemp.getText()).exists():
            self.kthmatempStatus.changeStatus("Προσβάσιμο", 'statusOk')
            state['kthmatemp_status'] = "Προσβάσιμο"
        else:
            self.kthmatempStatus.changeStatus("Μη Προσβάσιμο", 'statusError')
            state['kthmatemp_status'] = "Μη Προσβάσιμο"
        if Path(self.kthmadata.getText()).exists():
            self.kthmadataStatus.changeStatus("Προσβάσιμο", 'statusOk')
            state['kthmadata_status'] = "Προσβάσιμο"
            self.serverStatusChanged.emit(("Προσβάσιμο", 'statusOk'))
        else:
            self.kthmadataStatus.changeStatus("Μη Προσβάσιμο", 'statusError')
            state['kthmadata_status'] = "Μη Προσβάσιμο"
            self.serverStatusChanged.emit(("Μη Προσβάσιμο", 'statusError'))

    def areSettingsChanged(self):
        mel_changed = self.pickedMeleti != state['meleti']
        data_changed = self.kthmadata.getText() != state['kthmadata']
        temp_changed = self.kthmatemp.getText() != state['kthmatemp']
        fullname_changed = self.fullnameInsert.getText() != state['fullname']
        company_changed = self.companyInsert.getText() != state['company']
        if data_changed or temp_changed or mel_changed or fullname_changed or company_changed:
            self.saveButton.enable()
        else:
            self.saveButton.disable()

        self.checkServer()

    def onMeletiChanged(self):
        self.pickedMeleti = self.meletes.getCurrentText()
        self.meleti.setText(state[self.pickedMeleti]['name'])

        self.areSettingsChanged()
        self.status.disable()

    def onCreateMeletiChanged(self):
        mel = self.createMeletes.getCurrentText()
        if Path(f"C:/{mel}").exists():
            self.folderStatus.changeStatus("Προσβάσιμο", 'statusOk')
        else:
            self.folderStatus.changeStatus("Μη Προσβάσιμο", 'statusError')

    def onLicUpload(self):
        run_thread(threadpool=self.threadpool,
                   function=self.licUploadAction,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    def onCreateMeleti(self):
        run_thread(threadpool=self.threadpool,
                   function=self.createMeleti,
                   on_update=self.updateProgress,
                   on_result=self.updateResult,
                   on_finish=self.updateFinish)

    def licUploadAction(self, _progress):
        src = self.lic.getText()
        return load_lic(filepath=src, dst=paths.get_authfolder())

    @licensed(appname=state['appname'], category=state['meleti'])
    def createMeleti(self, _progress):
        meleti = self.createMeletes.getCurrentText()
        template_folder = paths.get_mel_template()
        return create_mel_folder(template_folder=template_folder,
                                 meleti=meleti)

    def onSave(self):
        state['meleti'] = self.meletes.getCurrentText()
        state['kthmatemp'] = self.kthmatemp.getText()
        state['kthmadata'] = self.kthmadata.getText()
        state['company'] = self.companyInsert.getText()
        state['fullname'] = self.fullnameInsert.getText()

        self.company.setText(state['company'])
        self.fullname.setText(state['fullname'])

        paths.set_attrs(state['meleti'], state['kthmadata'], state['kthmatemp'])

        state.update_db()
        self.saveButton.disable()

        self.updateJsonFile()

        self.settingsChanged.emit()

        self.popup.info("Οι ρυθμίσεις αποθηκεύτηκαν")

    def updateJsonFile(self):
        jsonfile = paths.get_arcgis_paths()
        jsondata = load_json(jsonfile)
        username = state['username']
        kthmatemp = state['kthmatemp'][0]
        kthmadata = state['kthmadata'][0]

        jsondata['temp'][username] = kthmatemp
        jsondata['data'][username] = kthmadata
        jsondata['users'][username] = username

        write_json(jsonfile, jsondata)


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
