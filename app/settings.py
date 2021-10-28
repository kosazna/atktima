# -*- coding: utf-8 -*-

APPNAME = "ktima"
VERSION = "10.1.1"
DEBUG = False
APPICON = "atktima.ico"
FONT = "Segoe UI"
FONTSIZE = 9

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
