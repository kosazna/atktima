# -*- coding: utf-8 -*-

from at.auth.client import Authorize, licensed

from atktima.path import paths
from atktima.settings import *

auth = Authorize(appname=APPNAME, auth_loc=paths.get_authfolder(), debug=DEBUG)
