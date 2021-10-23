# -*- coding: utf-8 -*-
import sys
from pathlib import Path
from typing import Tuple

import sip
from at.auth.client import licensed
from at.gui.button import Button
from at.gui.icons import *
from at.gui.label import Label
from at.gui.line import HLine
from at.gui.popup import Popup
from at.gui.selector import PathSelector
from at.gui.status import StatusLabel
from at.gui.utils import *
from at.logger import log
from at.utils import file_counter
from atktima.auth import licensed
from atktima.path import paths
from atktima.database import db
from atktima.state import state
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QWidget

# When setting fixed width to QLineEdit ->
# -> add alignment=Qt.AlignLeft when adding widget to layout

xmls = ('BLOCK_PNT_METADATA', 'GEO_METADATA', 'ROADS_METADATA')


class CountTab(QWidget):
    def __init__(self,
                 size: Tuple[Optional[int]] = (None, None),
                 parent: Optional[QWidget] = None,
                 *args,
                 **kwargs) -> None:
        super().__init__(parent=parent, *args, **kwargs)
        self.widgetMap = {}
        self.setupUi(size)
        self.pickedMeleti = state['meleti']
        self.threadpool = QThreadPool(parent=self)
        self.popup = Popup(state['appname'])
        self.missingShapes = []
        self.buttonCount.subscribe(self.countFiles)
        self.buttonMissing.subscribe(self.findMissingFiles)

    def setupUi(self, size):
        set_size(widget=self, size=size)

        layout = QVBoxLayout()
        layout.setContentsMargins(2,4,2,0)
        labelLayout = QHBoxLayout()
        countLayout = QHBoxLayout()
        self.shapeLayout = QVBoxLayout()
        self.shapeLayout.setContentsMargins(4, 2, 4, 2)
        self.shapeLayout.setSpacing(0)
        self.restLayout = QVBoxLayout()
        self.restLayout.setContentsMargins(4, 2, 4, 2)
        self.restLayout.setSpacing(0)
        self.restLayout.addStretch(0)

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

        path_mapping = {'LocalData': paths.get_localdata(),
                        'ParadosiData': paths.get_paradosidata()}
        self.folder = PathSelector(label="Φάκελος αρχείων",
                                   selectortype='folder_in',
                                   mapping=path_mapping,
                                   orientation=VERTICAL,
                                   combosize=(180, 24),
                                   labelsize=(None, 24),
                                   parent=self)

        self.buttonCount = Button(label='Καταμέτρηση',
                                  size=(180, 30),
                                  parent=self)
        self.buttonMissing = Button(label='Εύρεση κενών',
                                    size=(180, 30),
                                    parent=self)

        self.folder.setCurrentText('LocalData')

        for shape in db.get_shapes(state['meleti']):
            if shape != 'VSTEAS_REL':
                _widget = StatusLabel(label=shape, status='0',
                                      labelsize=(100, 18),
                                      statussize=(50, 18), parent=self)
                self.widgetMap[shape] = _widget
                self.shapeLayout.addWidget(_widget)
            else:
                _widget = StatusLabel(label=shape, status='0',
                                      labelsize=(140, 18),
                                      statussize=(50, 18), parent=self)
                self.widgetMap[shape] = _widget
                self.restLayout.addWidget(_widget)

        for xml in xmls:
            _widget = StatusLabel(label=xml, status='0',
                                  labelsize=(140, 18),
                                  statussize=(50, 18), parent=self)
            self.widgetMap[xml] = _widget
            self.restLayout.addWidget(_widget)

        self.buttonMissing.disable()

        labelLayout.addWidget(self.fullname)
        labelLayout.addWidget(self.username)
        labelLayout.addWidget(self.company, stretch=2, alignment=Qt.AlignLeft)
        labelLayout.addWidget(self.meleti)
        layout.addLayout(labelLayout)
        layout.addWidget(HLine())
        layout.addWidget(self.folder)
        countLayout.addLayout(self.shapeLayout)
        countLayout.addLayout(self.restLayout)
        layout.addLayout(countLayout)
        buttonLayout.addWidget(self.buttonCount)
        buttonLayout.addWidget(self.buttonMissing)
        layout.addWidget(HLine(), stretch=2, alignment=Qt.AlignTop)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def refreshShapes(self):
        for shape in self.widgetMap:
            if shape == 'VSTEAS_REL' or shape in xmls:
                self.restLayout.removeWidget(self.widgetMap[shape])
            else:
                self.shapeLayout.removeWidget(self.widgetMap[shape])
            sip.delete(self.widgetMap[shape])

        self.widgetMap = {}

        for shape in db.get_shapes(state['meleti']):
            if shape != 'VSTEAS_REL':
                _widget = StatusLabel(label=shape, status='0',
                                      labelsize=(100, 18),
                                      statussize=(50, 18), parent=self)
                self.widgetMap[shape] = _widget
                self.shapeLayout.addWidget(_widget)
            else:
                _widget = StatusLabel(label=shape, status='0',
                                      labelsize=(140, 18),
                                      statussize=(50, 18), parent=self)
                self.widgetMap[shape] = _widget
                self.restLayout.addWidget(_widget)

        for xml in xmls:
            _widget = StatusLabel(label=xml, status='0',
                                  labelsize=(140, 18),
                                  statussize=(50, 18), parent=self)
            self.widgetMap[xml] = _widget
            self.restLayout.addWidget(_widget)

    @licensed(appname=state['appname'], category=state['meleti'])
    def countFiles(self, *args, **kwargs):
        for shape in self.widgetMap:
            self.widgetMap[shape].setText('0')
        self.missingShapes = []

        folder = self.folder.getText()

        if folder and Path(folder).exists():
            all_folders = [p for p in Path(folder).iterdir() if p.is_dir()]
            folders_count = len(all_folders)
            filters = ('*.shp', '*.mdb', '*.xml')
            ext_access_names = ('.shp', '.mdb', '.xml')
            counter = file_counter(src=folder, filters=filters)

            for ext in ext_access_names:
                if ext in counter:
                    shapecount = counter[ext]
                    for shape in shapecount:
                        if shape in self.widgetMap:
                            num = str(shapecount[shape])
                            self.widgetMap[shape].setText(num)

                            if shapecount[shape] == folders_count:
                                self.widgetMap[shape].setStyle('statusOk')
                            elif num == 0:
                                self.widgetMap[shape].setStyle('statusError')
                            else:
                                self.widgetMap[shape].setStyle('statusWarning')
                                self.missingShapes.append(shape)

            for shape in self.widgetMap:
                if self.widgetMap[shape].getText() == '0':
                    self.widgetMap[shape].setStyle('statusError')

            if self.missingShapes:
                self.buttonMissing.enable()
        else:
            self.popup.error("Δώσε φάκελο για καταμέτρηση")

    @licensed(appname=state['appname'], category=state['meleti'])
    def findMissingFiles(self):
        if self.missingShapes:
            all_otas = db.get_ota_per_meleti(state['meleti'], 'NAMA')
            folder = self.folder.getText()
            for shape in sorted(self.missingShapes):
                all_file_parts = [p.parts for p in Path(
                    folder).glob(f'**/{shape}.*')]

                log.warning(f'\n[{shape}] Missing:')

                for ota in all_otas:
                    found = False
                    for parts in all_file_parts:
                        if ota in parts:
                            found = True
                            break

                    if not found:
                        log.info(f" - {ota}")
        else:
            self.popup.warning("Δεν έχει γίνει ακόμα καταμέτρηση")


if __name__ == '__main__':
    cssGuide = paths.get_css(obj=True).joinpath("_style.css").read_text()
    SEGOE = QFont("Segoe UI", 9)

    app = QApplication(sys.argv)
    app.setFont(SEGOE)
    app.setStyle('Fusion')

    ui = CountTab(size=(600, None))
    ui.setStyleSheet(cssGuide)
    ui.show()

    sys.exit(app.exec_())
