# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Union

import pandas as pd


def forest(claims: Union[str, Path],
           active_forest: Union[str, Path],
           output: Union[str, Path]):
    def make_owner(df):
        if df['TYPE'] == 0 and df['DASIKO'] == 0:
            return 0
        elif df['TYPE'] == 0 and df['DASIKO'] == 1:
            return 1
        elif df['TYPE'] == 1 and df['DASIKO'] == 0:
            return 2
        else:
            return 3

    diekdikisi = pd.read_excel(claims, dtype='string')
    dasika_energa = pd.read_excel(active_forest, dtype='string')

    diekdikisi = diekdikisi.astype({'AREA_MEAS': 'float64',
                                    'AREAFOREST': 'float64',
                                    'AREA_REST': 'float64',
                                    'TYPE': 'int64'})

    dasika_energa['KAEK'] = dasika_energa['KAEK'].str.replace('¿¿', 'ΕΚ')
    dasika_energa['DASIKO'] = 1

    forest = diekdikisi.merge(dasika_energa, how='left', on='KAEK')
    forest['DASIKO'] = forest['DASIKO'].fillna(0).astype(int)

    forest['OWNER'] = forest.apply(make_owner, axis=1)

    keep_cols = ["KAEK", "AREA_MEAS", "AREAFOREST", "AREA_REST", "OWNER"]

    final = forest[keep_cols].sort_values('KAEK').reset_index(
        drop=True).rename(columns={"AREAFOREST": "AREA_FOREST"})

    final.to_excel(output, index=False)
