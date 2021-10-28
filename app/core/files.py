# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Callable, Iterable, Optional, Union

from at.io.copyfuncs import copy_file
from at.result import Result
from at.text import replace_all


def get_shapes(src: Union[str, Path],
               dst: Union[str, Path],
               otas: Iterable[str],
               shapes: Iterable[str],
               src_schema: str,
               dst_schema: str,
               _progress: Optional[Callable] = None) -> Result:
    src_path = Path(src)
    dst_path = Path(dst)

    if _progress is not None:
        _progress.emit({'pbar_max': len(otas)})

    ota_counter = 0
    file_counter = 0

    for ota in otas:
        ota_counter += 1
        for shape in shapes:
            sub_src = replace_all(src_schema, {'shape': shape, 'ota': ota})
            sub_dst = replace_all(dst_schema,  {'shape': shape, 'ota': ota})

            if shape == 'VSTEAS_REL':
                _src = src_path.joinpath(f"{sub_src}/{shape}.mdb")
                _dst = dst_path.joinpath(f"{sub_dst}/{shape}.mdb")
            else:
                _src = src_path.joinpath(f"{sub_src}/{shape}.shp")
                _dst = dst_path.joinpath(f"{sub_dst}/{shape}.shp")

            copied = copy_file(_src, _dst)

            if copied:
                file_counter += 1

        if _progress is not None:
            _progress.emit({'pbar': ota_counter})

    if file_counter:
        return Result.success("Η αντιγραφή αρχείων ολοκληρώθηκε",
                              details={'secondary': f"Σύνολο αρχείων: {file_counter}"})
    return Result.warning("Δεν έγινε αντιγραφή για κανένα αρχείο")


def delete_files(src: Union[str, Path],
                 shapes: Iterable[str],
                 _progress: Optional[Callable] = None) -> Result:
    src_path = Path(src)
    _progress.emit({'pbar_max': len(shapes)})

    del_count = 0
    for idx, shape in enumerate(shapes, 1):
        for p in src_path.glob(shape):
            p.unlink(missing_ok=True)
            del_count += 1
        _progress.emit({'pbar': idx})

    if del_count:
        return Result.success(f"Έγινε διαγραφή {del_count} αρχείων")
    return Result.warning("Δεν διαγράφτηκε κανένα αρχείο")
