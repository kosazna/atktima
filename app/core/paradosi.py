# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Callable, Iterable, Optional, Union

from at.io.copyfuncs import copy_file
from at.io.utils import zip_file
from at.result import Result
from at.text import replace_all
from atktima.app.settings import *


def get_organized_server_files(src: Union[str, Path],
                               dst: Union[str, Path],
                               otas: Iterable[str],
                               _progress: Optional[Callable] = None) -> Result:

    src_path = Path(src)
    dst_path = Path(dst)

    zip_dst = dst_path.joinpath(databases)
    for p in src_path.glob('*.zip'):
        filename = p.stem
        if filename in otas:
            copy_file(p, zip_dst)

    geitones_src = src_path.joinpath('GEITONES')
    geitones_dst = dst_path.joinpath(f"{other}/GEITONES")
    copy_file(geitones_src, geitones_dst)

    forest_src = src_path.joinpath('FOREST')
    if forest_src.exists():
        forest_dst = dst_path.joinpath(f"{other}/FOREST")
        copy_file(forest_src, forest_dst)

    spatial_src = src_path.joinpath('SHAPE')
    if spatial_src.exists():
        _spatial = spatial_src
    else:
        _spatial = src_path.joinpath('ΧΩΡΙΚΑ')

    spatial_dst = dst_path.joinpath(spatial)

    for p in _spatial.iterdir():
        filename = p.stem
        if filename in otas:
            copy_file(p, spatial_dst, save_name=filename)


def get_unorganized_server_files(src: Union[str, Path],
                                 dst: Union[str, Path],
                                 otas: Iterable[str],
                                 local_schema: str,
                                 _progress: Optional[Callable] = None) -> Result:
    src_path = Path(src)
    dst_path = Path(dst)

    zip_dst = dst_path.joinpath(databases)
    other_dst = dst_path.joinpath(other)
    spatial_dst = dst_path.joinpath(spatial)

    zip_dst.mkdir(parents=True, exist_ok=True)

    for ota in otas:
        for p in src_path.glob(f"{ota}*.mdb"):
            filename = p.stem

            if 'FOREST' in filename:
                _dst = other_dst.joinpath('FOREST')
                copy_file(p, _dst)
            elif 'GEITONES' in filename:
                _dst = other_dst.joinpath('GEITONES')
                copy_file(p, _dst)
            elif 'VSTEAS_REL' in filename:
                sub_dst = replace_all(local_schema, {'shape': "VSTEAS_REL",
                                                     'ota': ota})
                _dst = spatial_dst.joinpath(sub_dst)
                copy_file(p, _dst, save_name='VSTEAS_REL')
            else:
                zip_file(p, zip_dst)


def create_empty_shapes(src: Union[str, Path],
                        dst: Union[str, Path],
                        otas: Iterable[str],
                        meleti_shapes: Iterable[str],
                        local_schema: str,
                        _progress: Optional[Callable] = None) -> Result:
    src_path = Path(src)
    dst_path = Path(dst)

    for p in src_path.glob('*.shp'):
        filename = p.stem

        if filename in meleti_shapes:
            for ota in otas:
                sub_dst = replace_all(local_schema, {'shape': filename,
                                                     'ota': ota})
                _dst = dst_path.joinpath(f"{sub_dst}/{filename}.shp")
                if not _dst.exists():
                    copy_file(p, _dst)
