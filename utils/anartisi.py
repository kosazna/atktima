# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Union

import pandas as pd
from at.io.copyfuncs import copy_file
from at.result import Result


def anartisi(src: Union[str, Path],
             dst: Union[str, Path],
             mapping_file: Union[str, Path],
             col_filename: str,
             col_region: str,
             col_page: str,
             col_tk: str,
             _progress: Callable):

    src_path = Path(src)
    dst_path = Path(dst)

    mapping = pd.read_excel(mapping_file)
    nfiles = mapping[col_filename].nunique()
    ntk = mapping[col_tk].nunique()

    if _progress is not None:
        _progress.emit(
            {'status': f"Σύνολο αποσπασμάτων: {nfiles} | Σύνολο TK: {ntk}"})

    all_files = tuple(src_path.glob('*.pdf'))

    if _progress is not None:
        _progress.emit({'pbar_max': len(all_files)})

    count = 0
    no_copy = []

    for p in all_files:
        filename = p.name
        stem = p.stem
        try:
            folders = mapping.loc[mapping[col_filename] == stem, [
                col_region, col_page, col_tk]].values.flatten().tolist()

            folders_path = "/".join(folders)
            final_dir = dst_path.joinpath(folders_path)
            final_dst = final_dir.joinpath(filename)

            copy_file(p, final_dst, copymode='fast')
            count += 1
            if _progress is not None:
                _progress.emit({'pbar': count})
        except Exception:
            no_copy.append(str(p))

    if no_copy:
        no_copy_files = '\n'.join(no_copy)
        return Result.warning('Η αντιγραφή αρχείων ολοκληρώθηκε. Κάποια αρχεία δεν αντιγράφηκαν',
                              details={'secondary': f"Πραγματοποιήθηκε αντιγραφή σε: [{count}]\nΔεν έγινε αντιγραφή (Show Details...)",
                                       'details': no_copy_files})
    else:
        return Result.success('Η αντιγραφή αρχείων ολοκληρώθηκε',
                              details={'secondary': f"'Πραγματοποιήθηκε αντιγραφή σε: [{count}]"})
