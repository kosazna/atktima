# -*- coding: utf-8 -*-

from at.auth.client import Authorize
from atktima.app.settings import *
from atktima.app.utils.path import paths
from dotenv import load_dotenv
import os

load_dotenv(paths.get_env())
TOKEN = os.getenv("GITHUB_TOKEN")

auth = Authorize(appname=APPNAME,
                 auth_loc=paths.get_authfolder(),
                 debug=DEBUG,
                 token=TOKEN)
