# -*- coding: utf-8 -*-

from at.path import PathEngine
from atktima.settings import *


class KtimaPaths(PathEngine):
    def __init__(self, appname: str = APPNAME):
        super().__init__(appname=appname)


paths = KtimaPaths(appname=APPNAME)
