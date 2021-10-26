# -*- coding: utf-8 -*-

APPNAME = "ktima"
VERSION = "10.1.1"
DEBUG = False
APPICON = "atktima.ico"
FONT = "Segoe UI"
FONTSIZE = 9

databases = "ΕΝΔΙΑΜΕΣΗ ΥΠΟΒΟΛΗ ΚΤΗΜΑΤΟΛΟΓΙΚΗΣ ΒΑΣΗΣ ΠΕΡΙΓΡΑΦΙΚΩΝ ΣΤΟΙΧΕΙΩΝ"
spatial = "ΕΝΔΙΑΜΕΣΗ ΥΠΟΒΟΛΗ ΚΤΗΜΑΤΟΛΟΓΙΚΗΣ ΒΑΣΗΣ ΧΩΡΙΚΩΝ ΣΤΟΙΧΕΙΩΝ"
other = "ΣΥΝΗΜΜΕΝΑ ΑΡΧΕΙΑ"

server_mapping = {"NAMA Server": '<ota>/SHP',
                  "2KP Server": '<ota>/SHP/<shape>',
                  "Άλλη παράδοση (ktima11)": '<ota>/SHAPE/<shape>',
                  "Άλλη παράδοση (ktima16)": '<ota>/<shape>'}

local_mapping = {"ktima16": '<ota>/<shape>',
                 "ktima11": '<ota>/SHAPE/<shape>'}

metadata_mapping = {"ktima16": '<ota>',
                    "ktima11": '<ota>/METADATA'}
