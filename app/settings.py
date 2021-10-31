# -*- coding: utf-8 -*-

from at.utils import user
from pathlib import Path

APPNAME = "ktima"
VERSION = "10.1.1"
DEBUG = False
USERNAME = user()
FONT = "Segoe UI"
FONTSIZE = 9
ICONNAME = "atktima.ico"

if Path(f"C:/Users/{USERNAME}/.ktima/static/atktima.ico").exists():
    APPICON = f"C:/Users/{USERNAME}/.ktima/static/{ICONNAME}"
else:
    APPICON = ICONNAME

DATABASES = "ΕΝΔΙΑΜΕΣΗ ΥΠΟΒΟΛΗ ΚΤΗΜΑΤΟΛΟΓΙΚΗΣ ΒΑΣΗΣ ΠΕΡΙΓΡΑΦΙΚΩΝ ΣΤΟΙΧΕΙΩΝ"
SPATIAL = "ΕΝΔΙΑΜΕΣΗ ΥΠΟΒΟΛΗ ΚΤΗΜΑΤΟΛΟΓΙΚΗΣ ΒΑΣΗΣ ΧΩΡΙΚΩΝ ΣΤΟΙΧΕΙΩΝ"
OTHER = "ΣΥΝΗΜΜΕΝΑ ΑΡΧΕΙΑ"

SERVER_MAPPING = {"NAMA Server": '<ota>/SHP',
                  "2KP Server": '<ota>/SHP/<shape>',
                  "Άλλη παράδοση (ktima11)": '<ota>/SHAPE/<shape>',
                  "Άλλη παράδοση (ktima16)": '<ota>/<shape>'}

LOCAL_MAPPING = {"ktima16": '<ota>/<shape>',
                 "ktima11": '<ota>/SHAPE/<shape>'}

METADATA_MAPPING = {"ktima16": '<ota>',
                    "ktima11": '<ota>/METADATA'}
