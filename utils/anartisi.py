# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Union

import pandas as pd
from at.io.copyfuncs import copy_file


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

    with ThreadPoolExecutor() as executor:
        for p in all_files:
            count += 1
            filename = p.name
            stem = p.stem

            try:
                folders = mapping.loc[mapping[col_filename] == stem, [
                    col_region, col_page, col_tk]].values.flatten().tolist()

                folders_path = "/".join(folders)
                final_dir = dst_path.joinpath(folders_path)
                final_dst = final_dir.joinpath(filename)

                executor.submit(copy_file, p, final_dst, None, 'fast')
                if _progress is not None:
                    _progress.emit({'pbar': count})
            except Exception:
                pass

        if _progress is not None:
            _progress.emit(
                {'status': "Η διαδικασία τρέχει ακόμα στο παρασκήνιο"})
