# -*- coding: utf-8 -*-

from at.utils import user
from pathlib import Path

APPNAME = "ktima"
VERSION = "10.2.1"
DEBUG = False
USERNAME = user()
FONT = "Segoe UI"
FONTSIZE = 9
ICONNAME = "ktima.ico"

if Path(f"C:/Users/{USERNAME}/.ktima/static/{ICONNAME}").exists():
    APPICON = f"C:/Users/{USERNAME}/.ktima/static/{ICONNAME}"
else:
    APPICON = ICONNAME

DATABASES = "ΕΝΔΙΑΜΕΣΗ ΥΠΟΒΟΛΗ ΚΤΗΜΑΤΟΛΟΓΙΚΗΣ ΒΑΣΗΣ ΠΕΡΙΓΡΑΦΙΚΩΝ ΣΤΟΙΧΕΙΩΝ"
SPATIAL = "ΕΝΔΙΑΜΕΣΗ ΥΠΟΒΟΛΗ ΚΤΗΜΑΤΟΛΟΓΙΚΗΣ ΒΑΣΗΣ ΧΩΡΙΚΩΝ ΣΤΟΙΧΕΙΩΝ"
OTHER = "ΣΥΝΗΜΜΕΝΑ ΑΡΧΕΙΑ"

SERVER_MAPPING = {"NAMA Server": '<ota>/SHP',
                  "2KP Server": '<ota>/SHP/<shape>',
                  "ktima11 - Άλλη παράδοση": '<ota>/SHAPE/<shape>',
                  "ktima16 - Άλλη παράδοση": '<ota>/<shape>'}

LOCAL_MAPPING = {"ktima16": '<ota>/<shape>',
                 "ktima11": '<ota>/SHAPE/<shape>'}

METADATA_MAPPING = {"ktima16": '<ota>',
                    "ktima11": '<ota>/METADATA'}

ORGANIZE_FILTER = {"Ανακτήσεις": '.zip',
                   "Σαρωμένα - Δηλώσεις": '.tif|.tiff',
                   "Σαρωμένα - Έγγραφα": '.tif|.tiff',
                   "Excel": '.xls|.xlsx',
                   "ktima16 - Φάκελοι": '.shp',
                   "ktima11 - Φάκελοι": '.shp',
                   "ΟΤΑ_Shape": '.shp',
                   "ΟΤΑ-Shape": '.shp'}

ORGANIZE_READ_SCHEMA = {"Ανακτήσεις": '<ota@10:14>',
                        "Σαρωμένα - Δηλώσεις": '<ota@2:6>',
                        "Σαρωμένα - Έγγραφα": '<ota@1:5>',
                        "Excel": '<ota>-',
                        "ktima16 - Φάκελοι": '<ota$2><shape$1>',
                        "ktima11 - Φάκελοι": '<ota$3><shape$1>',
                        "ΟΤΑ_Shape": "<ota>_<shape>",
                        "ΟΤΑ-Shape": "<ota>-<shape>"}

ORGANIZE_SAVE_SCHEMA = {"Ανά ΟΤΑ": '<ota>',
                        "ktima16 - Χωρικά": '<ota>/<shape>',
                        "ktima11 - Χωρικά": '<ota>/SHAPE/<shape>'}
