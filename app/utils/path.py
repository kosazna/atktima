# -*- coding: utf-8 -*-

from typing import Optional
from at.path import PathEngine
from pathlib import Path
from atktima.app.settings import *


class KtimaPaths(PathEngine):
    kthmadata: Optional[Path] = None
    kthmatemp: Optional[Path] = None
    meleti: Optional[Path] = None

    def __init__(self, appname: str = APPNAME):
        super().__init__(appname=appname)

    @classmethod
    def set_attrs(cls, meleti: str, kthmadata: str, kthmatemp: str):
        cls.meleti = Path(f"C:/{meleti}")
        cls.kthmadata = Path(kthmadata)
        cls.kthmatemp = Path(kthmatemp)

    def get_meleti(self, obj: bool = False):
        if self.meleti is None:
            return self.get_cwd(obj=obj)
        if obj:
            return self.meleti
        return self.meleti.as_posix()

    def get_kthmadata(self, obj: bool = False):
        if self.kthmadata is None:
            return self.get_cwd(obj=obj)
        if obj:
            return self.kthmadata
        return self.kthmadata.as_posix()

    def get_kthmatemp(self, obj: bool = False):
        if self.kthmatemp is None:
            return self.get_cwd(obj=obj)
        if obj:
            return self.kthmatemp
        return self.kthmatemp.as_posix()

    def get_localdata(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!OutputData/LocalData")

        if obj:
            return _path
        return _path.as_posix()

    def get_paradosidata(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!OutputData/ParadosiData")

        if obj:
            return _path
        return _path.as_posix()

    def get_json_status(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!InputData/Docs/KT_Status.json")

        if obj:
            return _path
        return _path.as_posix()

    def get_empty_shapes(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!InputData/Shapefiles/Empty_Shapefiles")

        if obj:
            return _path
        return _path.as_posix()

    def get_metadata(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!InputData/XML_Prototypes")

        if obj:
            return _path
        return _path.as_posix()

    def get_databases(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("Geodatabases")

        if obj:
            return _path
        return _path.as_posix()

    def get_mel_template(self, obj: bool = False):
        _path = self.get_kthmatemp(obj=True).joinpath("! aznavouridis.k/Diafora/ktima")

        if obj:
            return _path
        return _path.as_posix()

    def get_anaktiseis_in(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!InputData/Anaktiseis")

        if obj:
            return _path
        return _path.as_posix()
    
    def get_anaktiseis_out(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!OutputData/Anaktiseis")

        if obj:
            return _path
        return _path.as_posix()

    def get_saromena_in(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!InputData/Saromena")

        if obj:
            return _path
        return _path.as_posix()
    
    def get_saromena_out(self, obj: bool = False):
        _path = self.get_meleti(obj=True).joinpath("!OutputData/Saromena")

        if obj:
            return _path
        return _path.as_posix()


paths = KtimaPaths(appname=APPNAME)
