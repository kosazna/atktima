# -*- coding: utf-8 -*-
import sys
from os import path
from pathlib import Path
from time import sleep
from typing import Any, Optional, Tuple, Union

import pandas as pd
from at.auth.client import Authorize, AuthStatus, licensed
from at.auth.utils import load_lic
from at.gui.components import *
from at.gui.utils import HORIZONTAL, VERTICAL, set_size
from at.gui.worker import run_thread
from at.io.copyfuncs import batch_copy_file, copy_file
from at.logger import log
from at.path import PathEngine
from at.result import Result
from atktima.app.core import (create_empty_shapes, create_metadata,
                              get_organized_server_files, get_shapes,
                              get_unorganized_server_files)
from atktima.app.settings import *
from atktima.app.utils import db, paths, state
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout


class ParadosiTab(QWidget):
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

    def setupUi(self, size):
        set_size(widget=self, size=size)
        path_mapping = {'ParadosiData': paths.get_paradosidata()}

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 4, 2, 0)
        labelLayout = QHBoxLayout()
        mdbLayout = QHBoxLayout()
        metadataLayout = QHBoxLayout()
        listLayout = QHBoxLayout()
        buttonLayout = QHBoxLayout()

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
        self.mdbFolder = FolderInput(label="Βάσεις",
                                     labelsize=(90, 24),
                                     parent=self)
        self.checkMdbOrganized = CheckInput(label="Οργανωμένες",
                                            checked=False,
                                            parent=self)
        self.dateMetadata = StrInput(label='Ημερομηνία Metadata',
                                     labelsize=(135, 24),
                                     editsize=(100, 24),
                                     parent=self)
        self.selectorMetadata = StrSelector(label="Δομή Metadata",
                                            labelsize=(90, 24),
                                            editsize=(200, 24),
                                            mapping=metadata_mapping,
                                            parent=self)
        self.selectorSpatial = StrSelector(label="Δομή Χωρικών",
                                           labelsize=(90, 24),
                                           editsize=(200, 24),
                                           mapping=local_mapping,
                                           parent=self)
        self.folderOutput = PathSelector(label="Φάκελος που θα δημιουργηθεί η παράδοση",
                                         selectortype='folder_in',
                                         mapping=path_mapping,
                                         orientation=VERTICAL,
                                         combosize=(180, 24),
                                         labelsize=(None, 24),
                                         parent=self)
        self.shape = ListWidget(label="Επιλογή Χωρικών",
                                widgetsize=(None, 200),
                                parent=self)
        self.otas = ListWidget(label="Επιλογή ΟΤΑ",
                               widgetsize=(None, 200),
                               parent=self)
        self.makeAll = Button("Φόρτωση Όλων",
                              color='blue',
                              size=(130, 30),
                              parent=self)
        self.makeSpatial = Button("Φόρτωση Χωρικών",
                                  size=(130, 24),
                                  parent=self)
        self.makeEmpty = Button("Φόρτωση Κενών",
                                size=(130, 24),
                                parent=self)
        self.makeMetadata = Button("Φόρτωση Metadata",
                                   size=(130, 24),
                                   parent=self)
        self.makeMdbs = Button("Φόρτωση Βάσεων",
                               size=(130, 24),
                               parent=self)
        self.progress = ProgressBar(parent=self)
        self.status = StatusButton(parent=self)

        self.dateMetadata.setPlaceholder("dd/mm/yyyy")
        self.folderOutput.setCurrentText("ParadosiData")
        selectorsKey = state[state['meleti']]['type']
        self.selectorMetadata.setCurrentText(selectorsKey)
        self.selectorSpatial.setCurrentText(selectorsKey)
        self.shape.addItems(db.get_shapes(state['meleti']))
        self.otas.addItems(db.get_ota_per_meleti_company(
            state['meleti'], state['company']))
        self.shape.hideButtons()
        self.otas.hideButtons()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.folderOutput)
        layout.addWidget(HLine())
        listLayout.addWidget(self.shape)
        listLayout.addWidget(self.otas)
        layout.addLayout(listLayout)
        layout.addWidget(HLine())
        mdbLayout.addWidget(self.mdbFolder)
        mdbLayout.addWidget(self.checkMdbOrganized)
        layout.addLayout(mdbLayout)
        metadataLayout.addWidget(self.selectorMetadata)
        metadataLayout.addWidget(self.dateMetadata,
                                 stretch=2, alignment=Qt.AlignLeft)
        layout.addLayout(metadataLayout)
        layout.addWidget(self.selectorSpatial)
        layout.addWidget(HLine())
        buttonLayout.addWidget(self.makeAll)
        buttonLayout.addWidget(self.makeSpatial)
        buttonLayout.addWidget(self.makeMdbs)
        buttonLayout.addWidget(self.makeEmpty)
        buttonLayout.addWidget(self.makeMetadata)
        layout.addLayout(buttonLayout)
        layout.addWidget(HLine(), stretch=2, alignment=Qt.AlignTop)
        layout.addWidget(self.progress)
        layout.addWidget(self.status)

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
    
    @licensed(appname=state['appname'], category=state['meleti'])
    def loadAll(self, _progress):
        actions = {'loadSpatial': None,
                   'loadMdbs': None,
                   'loadEmpty': None,
                   'loadMetadata': None}

        actions['loadSpatial'] = self.loadSpatial(_progress)
        actions['loadMdbs'] = self.loadMdbs(_progress)
        actions['loadEmpty'] = self.loadEmpty(_progress)
        actions['loadMetadata'] = self.loadMetadata(_progress)
        
    @licensed(appname=state['appname'], category=state['meleti'])
    def loadSpatial(self, _progress):
        local_folder = paths.get_localdata()
        paradosi_folder = self.folderOutput.getText()

        struct_key = state[state['meleti']]['type']
        local_structure = local_mapping[struct_key]
        paradosi_structure = self.selectorSpatial.getText()

        user_shapes = self.shape.getCheckState()
        user_otas = self.otas.getCheckState()

        if user_otas and user_shapes:
            return get_shapes(src=local_folder,
                              dst=paradosi_folder,
                              otas=user_otas,
                              shapes=user_shapes,
                              server_schema=local_structure,
                              local_schema=paradosi_structure,
                              _progress=_progress)
        else:
            return Result.warning('Δεν βρέθηκε επιλογή για κάποια κατηγορία')

    @licensed(appname=state['appname'], category=state['meleti'])
    def loadMdbs(self, _progress):
        mdb_folder = self.mdbFolder.getText()
        paradosi_folder = self.folderOutput.getText()
        are_organized = self.checkMdbOrganized.isChecked()
        user_otas = self.otas.getCheckState()
        paradosi_structure = self.selectorSpatial.getText()

        if are_organized:
            return get_organized_server_files(src=mdb_folder,
                                              dst=paradosi_folder,
                                              otas=user_otas,
                                              _progress=_progress)
        else:
            return get_unorganized_server_files(src=mdb_folder,
                                                dst=paradosi_folder,
                                                otas=user_otas,
                                                local_schema=paradosi_structure,
                                                _progress=_progress)

    @licensed(appname=state['appname'], category=state['meleti'])
    def loadEmpty(self, _progress):
        empty_folder = paths.get_empty_shapes()
        paradosi_folder = self.folderOutput.getText()
        user_otas = self.otas.getCheckState()
        shapes = db.get_shapes(state['meleti'])
        paradosi_structure = self.selectorSpatial.getText()

        return create_empty_shapes(src=empty_folder,
                                   dst=paradosi_folder,
                                   otas=user_otas,
                                   meleti_shapes=shapes,
                                   local_schema=paradosi_structure,
                                   _progress=_progress)

    @licensed(appname=state['appname'], category=state['meleti'])
    def loadMetadata(self, _progress):
        metadata_folder = paths.get_metadata()
        paradosi_folder = self.folderOutput.getText()
        user_otas = self.otas.getCheckState()
        paradosi_structure = self.selectorSpatial.getText()

        return create_empty_shapes(src=metadata_folder,
                                   dst=paradosi_folder,
                                   otas=user_otas,
                                   metadata_schema=paradosi_structure,
                                   _progress=_progress)


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = ParadosiTab(size=(None, 600))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
