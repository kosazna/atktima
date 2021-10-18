# -*- coding: utf-8 -*-

from typing import Optional
from at.path import PathEngine
from pathlib import Path
from atktima.settings import *


class KtimaPaths(PathEngine):
    kthmadata: Optional[Path] = None
    kthmatemp: Optional[Path] = None
    meleti: Optional[Path] = None

    def __init__(self, appname: str = APPNAME):
        super().__init__(appname=appname)

    @classmethod
    def set_meleti(cls, meleti: str, kthmadata: str, kthmatemp: str):
        cls.meleti = Path(f"C:/{meleti}")
        cls.kthmadata = Path(kthmadata)
        cls.kthmatemp = Path(kthmatemp)

    def get_kthmadata(self, obj: bool = False):
        if obj:
            return self.kthmadata
        return self.kthmadata.as_posix()

    def get_localdata(self, obj: bool = False):
        _path = self.meleti.joinpath("!OutputData/LocalData")

        if obj:
            return _path
        return _path.as_posix()


paths = KtimaPaths(appname=APPNAME)
