# -*- coding: utf-8 -*-

from at.state import State
from atktima.settings import *
from atktima.database import db


state = State.from_db(db)
state.set({'appname': APPNAME, 'version': VERSION, 'debug': DEBUG})
