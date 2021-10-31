# -*- coding: utf-8 -*-
import sys
from typing import Optional, Tuple

from at.gui.components import Console
from at.gui.utils import set_size
from at.logger import log
from atktima.app.interface import (AnartisiTab, CountTab, FilesTab, MiscTab,
                                   OrganizeTab, ParadosiTab, SettingsTab)
from atktima.app.utils import auth, db, paths, state
from PyQt5.QtCore import Qt, QThreadPool, pyqtSlot
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QTabWidget,
                             QVBoxLayout, QWidget)


cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
paths.set_attrs(state['meleti'], state['kthmadata'], state['kthmatemp'])


class KtimaUI(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.setupUi(size)
        self.threadpool = QThreadPool(parent=self)
        self.settingsTab.settingsChanged.connect(self.onSettingsUpdate)
        self.settingsTab.serverStatusChanged.connect(self.onServerStatusChanged)
        self.check_auth()

    def setupUi(self, size):
        self.setObjectName("MainWidget")
        self.setStyleSheet(cssGuide)
        self.setWindowTitle(f"{state['appname']}")
        self.move(260, 150)

        set_size(widget=self, size=size)

        self.appLayout = QHBoxLayout()

        self.console = Console(size=(700, None), parent=self)

        self.tabs = QTabWidget(parent=self)
        self.tabs.setDocumentMode(True)

        self.settingsTab = SettingsTab(size=(700, None), parent=self)
        self.tabs.addTab(self.settingsTab, "Ρυθμίσεις")
        self.filesTab = FilesTab(size=(700, None), parent=self)
        self.tabs.addTab(self.filesTab, "Ενημέρωση")
        self.countTab = CountTab(size=(700, None), parent=self)
        self.tabs.addTab(self.countTab, "Καταμέτρηση")
        self.paradosiTab = ParadosiTab(size=(700, None), parent=self)
        self.tabs.addTab(self.paradosiTab, "Παράδοση")
        self.anartisiTab = AnartisiTab(size=(700, None), parent=self)
        self.tabs.addTab(self.anartisiTab, "Ανάρτηση")
        self.organizeTab = OrganizeTab(size=(700, None), parent=self)
        self.tabs.addTab(self.organizeTab, "Οργάνωση")
        self.miscTab = MiscTab(size=(700, None), parent=self)
        self.tabs.addTab(self.miscTab, "Διάφορα")

        self.appLayout.addWidget(self.tabs)
        self.appLayout.addWidget(self.console)

        self.tabs.setCurrentIndex(0)

        self.setLayout(self.appLayout)

    @pyqtSlot()
    def onSettingsUpdate(self):
        mel_shapes = db.get_shapes(state['meleti'])
        mel_otas = db.get_ota_per_meleti_company(state['meleti'],
                                                 state['company'])
        melType = state[state['meleti']]['type']

        all_path_mapping = {'LocalData': paths.get_localdata(),
                            'ParadosiData': paths.get_paradosidata(),
                            'Other...': ''}
        paradosi_path_mapping = {'ParadosiData': paths.get_paradosidata(),
                                 'Other...': ''}

        self.filesTab.meleti.setText(state['meleti'])
        self.filesTab.fullname.setText(state['fullname'])
        self.filesTab.company.setText(state['company'])
        self.filesTab.shape.clearContent()
        self.filesTab.shape.addItems(mel_shapes)
        self.filesTab.otas.clearContent()
        self.filesTab.otas.addItems(mel_otas)
        self.filesTab.localWidget.setCurrentText(melType)

        self.countTab.meleti.setText(state['meleti'])
        self.countTab.fullname.setText(state['fullname'])
        self.countTab.company.setText(state['company'])
        self.countTab.refreshShapes()
        self.countTab.folder.clearItems()
        self.countTab.folder.addItems(all_path_mapping)

        self.organizeTab.meleti.setText(state['meleti'])
        self.organizeTab.fullname.setText(state['fullname'])
        self.organizeTab.company.setText(state['company'])

        self.paradosiTab.meleti.setText(state['meleti'])
        self.paradosiTab.fullname.setText(state['fullname'])
        self.paradosiTab.company.setText(state['company'])
        self.paradosiTab.folderOutput.clearItems()
        self.paradosiTab.folderOutput.addItems(paradosi_path_mapping)
        self.paradosiTab.shape.clearContent()
        self.paradosiTab.shape.addItems(mel_shapes)
        self.paradosiTab.otas.clearContent()
        self.paradosiTab.otas.addItems(mel_otas)
        self.paradosiTab.selectorMetadata.setCurrentText(melType)
        self.paradosiTab.selectorSpatial.setCurrentText(melType)

        self.anartisiTab.meleti.setText(state['meleti'])
        self.anartisiTab.fullname.setText(state['fullname'])
        self.anartisiTab.company.setText(state['company'])

        self.miscTab.meleti.setText(state['meleti'])
        self.miscTab.fullname.setText(state['fullname'])
        self.miscTab.company.setText(state['company'])
        self.miscTab.shape.clearContent()
        self.miscTab.shape.addItems(mel_shapes)
        self.miscTab.otas.clearContent()
        self.miscTab.otas.addItems(mel_otas)
        self.miscTab.schema.setCurrentText(melType)

        self.check_auth()

    @pyqtSlot(tuple)
    def onServerStatusChanged(self, status):
        self.filesTab.server.changeStatus(*status)

    def check_auth(self):
        status, info = auth.is_licensed(category=state['meleti'])
        auth.change_user_auth(status)
        if status:
            log.success(f"{info} for {state['meleti']}")
        else:
            log.error(f"{info} for {state['meleti']}")


if __name__ == '__main__':

    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = KtimaUI(size=(None, 600))
    ui.show()

    sys.exit(app.exec_())
