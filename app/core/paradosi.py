# -*- coding: utf-8 -*-
import re
from pathlib import Path
from typing import Callable, Iterable, Optional, Union

from at.io.copyfuncs import copy_file
from at.io.object import FilterObject
from at.io.utils import zip_file
from at.result import Result
from at.text import replace_all
from atktima.app.settings import *


def get_organized_server_files(src: Union[str, Path],
                               dst: Union[str, Path],
                               otas: Iterable[str],
                               all_otas=Iterable[str],
                               _progress: Optional[Callable] = None) -> Result:

    src_path = Path(src)
    dst_path = Path(dst)

    zip_dst = dst_path.joinpath(DATABASES)
    zip_files = list(src_path.glob('*.zip'))
    _progress.emit({'pbar_max': len(zip_files),
                    'pbar': 0,
                    'status': 'Αντιγραφή αρχείων zip'})
    for idx, p in enumerate(zip_files, 1):
        filename = p.stem
        if filename in otas:
            copy_file(p, zip_dst)
            _progress.emit({'pbar': idx})

    ignored_otas = FilterObject(
        filters=[ota for ota in all_otas if ota not in otas])

    _progress.emit({'status': 'Αντιγραφή mdb: GEITONES'})
    geitones_src = src_path.joinpath('GEITONES')
    geitones_dst = dst_path.joinpath(f"{OTHER}")
    copy_file(geitones_src, geitones_dst, ignore=ignored_otas)

    forest_src = src_path.joinpath('FOREST')
    if forest_src.exists():
        _progress.emit({'status': 'Αντιγραφή mdb: FOREST'})
        forest_dst = dst_path.joinpath(f"{OTHER}")
        copy_file(forest_src, forest_dst, ignore=ignored_otas)

    spatial_src = src_path.joinpath('SHAPE')
    if spatial_src.exists():
        _spatial = spatial_src
    else:
        _spatial = src_path.joinpath('ΧΩΡΙΚΑ')

    spatial_dst = dst_path.joinpath(SPATIAL)

    spatial_files = list(_spatial.iterdir())
    _progress.emit({'pbar_max': len(spatial_files),
                    'pbar': 0,
                    'status': 'Αντιγραφή χωρικών αρχείων'})
    for idx, p in enumerate(spatial_files, 1):
        filename = p.stem
        if filename in otas:
            copy_file(p, spatial_dst, save_name=filename)
            _progress.emit({'pbar': idx})

    _progress.emit({'status': 'Οι βάσεις οργανώθηκαν'})


def get_unorganized_server_files(src: Union[str, Path],
                                 dst: Union[str, Path],
                                 otas: Iterable[str],
                                 local_schema: str,
                                 _progress: Optional[Callable] = None) -> Result:
    src_path = Path(src)
    dst_path = Path(dst)

    zip_dst = dst_path.joinpath(DATABASES)
    other_dst = dst_path.joinpath(OTHER)
    spatial_dst = dst_path.joinpath(SPATIAL)

    zip_dst.mkdir(parents=True, exist_ok=True)

    _progress.emit({'pbar_max': len(otas),
                    'pbar': 0,
                    'status': 'Γίνεται οργάνωση των βάσεων'})
    for idx, ota in enumerate(otas, 1):
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
                copy_file(p, spatial_dst)
        _progress.emit({'pbar': idx})

    _progress.emit({'status': 'Οι βάσεις οργανώθηκαν'})


def create_empty_shapes(src: Union[str, Path],
                        dst: Union[str, Path],
                        otas: Iterable[str],
                        meleti_shapes: Iterable[str],
                        local_schema: str,
                        _progress: Optional[Callable] = None) -> Result:
    src_path = Path(src)
    dst_path = Path(dst)

    _progress.emit({'pbar_max': 100,
                    'pbar': 0,
                    'status': 'Γίνεται δημιουργία των κενών αρχείων'})

    for p in src_path.glob('**/*.shp'):
        filename = p.stem
        if filename in meleti_shapes:
            for ota in otas:
                sub_dst = replace_all(local_schema, {'shape': filename,
                                                     'ota': ota})
                _dst = dst_path.joinpath(f"{sub_dst}")

                if not _dst.exists():
                    copy_file(p, _dst, copymode='fast')

    _progress.emit({'status': 'Τα κενά αρχεία δημιουργήθηκαν'})


def create_metadata(src: Union[str, Path],
                    dst: Union[str, Path],
                    date: str,
                    otas: Iterable[str],
                    metadata_schema: str,
                    _progress: Optional[Callable] = None) -> Result:
    src_path = Path(src)
    dst_path = Path(dst)

    ota_re = re.compile(r'(<CODE_OKXE>)(\d*)(</CODE_OKXE>)')
    date_re = re.compile(r'(<DeliveryDate>)(\d*/\d*/\d*)(</DeliveryDate>)')

    _progress.emit({'pbar_max': len(otas),
                    'pbar': 0,
                    'status': 'Γίνεται δημιουργία των metadata'})

    metadatas = {}
    for p in src_path.glob('*.xml'):
        filename = p.stem
        metadatas[filename] = p.read_text(encoding='utf-8-sig')

    for idx, ota in enumerate(otas, 1):
        sub_dst = replace_all(metadata_schema, {'ota': ota})
        _dst = dst_path.joinpath(sub_dst)
        _dst.mkdir(parents=True, exist_ok=True)

        for metadata in metadatas:
            _meta = metadatas[metadata]
            _meta = ota_re.sub(f'\g<1>{ota}\g<3>', _meta)
            _meta = date_re.sub(f'\g<1>{date}\g<3>', _meta)

            _dst.joinpath(f"{metadata}.xml").write_text(_meta,
                                                        encoding='utf-8-sig')
        _progress.emit({'pbar': idx})

    _progress.emit({'status': 'Τα metadata δημιουργήθηκαν'})
