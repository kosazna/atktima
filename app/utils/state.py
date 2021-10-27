# -*- coding: utf-8 -*-

from at.state import State
from atktima.app.settings import *
from atktima.app.utils.database import db
from pprint import pprint

state = State.from_db(db)
state.set({'appname': APPNAME, 'version': VERSION, 'debug': DEBUG})
