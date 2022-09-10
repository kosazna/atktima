# -*- coding: utf-8 -*-

from at.state import State
from atktima.app.settings import *
from atktima.app.utils.database import db
# from atktima.app.utils.path import paths
from pprint import pprint

state = State.from_db(db)
state.set({'appname': APPNAME, 'version': VERSION, 'debug': DEBUG})


# state = AppState(appname=APPNAME,
#                  version=VERSION,
#                  debug=DEBUG,
#                  db=db,
#                  json=paths.get_arcgis_paths())

# print(state.json.state)