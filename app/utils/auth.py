# -*- coding: utf-8 -*-

from at.auth.client import Authorize

from atktima.app.utils.path import paths
from atktima.app.settings import *

auth = Authorize(appname=APPNAME, auth_loc=paths.get_authfolder(), debug=DEBUG)
