# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Callable, Iterable, Optional, Union

import pandas as pd
from at.result import Result
from at.text import replace_all


def forest(claims: Union[str, Path],
           active_forest: Union[str, Path],
           output: Union[str, Path],
           _progress: Optional[Callable] = None):
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

    _progress.emit(
        {'status': f"Διεκδίκηση σε: {diekdikisi.shape[0]} | ΚΑΕΚ με δασικό: {dasika_energa.shape[0]}"})

    dasika_energa['KAEK'] = dasika_energa['KAEK'].str.replace('¿¿', 'ΕΚ')
    dasika_energa['DASIKO'] = 1

    forest = diekdikisi.merge(dasika_energa, how='left', on='KAEK')
    forest['DASIKO'] = forest['DASIKO'].fillna(0).astype(int)

    forest['OWNER'] = forest.apply(make_owner, axis=1)

    keep_cols = ["KAEK", "AREA_MEAS", "AREAFOREST", "AREA_REST", "OWNER"]

    final = forest[keep_cols].sort_values('KAEK').reset_index(
        drop=True).rename(columns={"AREAFOREST": "AREA_FOREST"})

    final.to_excel(output, index=False)


def make_folders(dst: Union[str, Path],
                 otas: Iterable[str],
                 shapes: Iterable[str],
                 dst_schema: str,
                 _progress: Optional[Callable] = None) -> Result:
    dst_path = Path(dst)
    folder_count = 0

    for ota in otas:
        for shape in shapes:
            sub_dst = replace_all(dst_schema,  {'shape': shape, 'ota': ota})
            _dst = dst_path.joinpath(sub_dst)
            _dst.mkdir(parents=True, exist_ok=True)
            folder_count += 1
    
    if folder_count:
        return Result.success("Η δημιουργία φακέλων ολοκληρώθηκε",
                              details={'secondary': f"Σύνολο φακέλων: {folder_count}"})
    return Result.warning("Δεν έγινε δημιουργία για κανένα φάκελο")
