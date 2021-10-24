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


paths = KtimaPaths(appname=APPNAME)