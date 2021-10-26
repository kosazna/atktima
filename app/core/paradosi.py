# -*- coding: utf-8 -*-
import re
from pathlib import Path
from typing import Callable, Iterable, Optional, Union

from at.io.copyfuncs import copy_file
from at.io.utils import zip_file
from at.result import Result
from at.text import replace_all
from atktima.app.settings import *

ot = [
    "22003",
    "22006",
    "22008",
    "22011",
    "22012",
    "22019",
    "22022",
    "22033",
    "22044",
    "22049",
    "22050",
    "22055",
    "22057",
    "22058",
    "22059",
    "22062",
    "22063",
    "22066",
    "22070",
    "22071",
    "22076",
    "22085",
    "22093",
    "22095",
    "22098",
    "22100",
    "22101",
    "22103",
    "22104",
    "22105",
    "22106",
    "22107",
    "22110",
    "22116",
    "22123",
    "22125",
    "22126",
    "22129",
    "22132",
    "22134",
    "22140",
    "22141"]


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

    for p in src_path.glob('**/*.shp'):
        filename = p.stem
        if filename in meleti_shapes:
            for ota in otas:
                sub_dst = replace_all(local_schema, {'shape': filename,
                                                     'ota': ota})
                _dst = dst_path.joinpath(f"{sub_dst}/{filename}.shp")
                
                if not _dst.exists():
                    copy_file(p, _dst)


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

    metadatas = {}
    for p in src_path.glob('*.xml'):
        filename = p.stem
        metadatas[filename] = p.read_text(encoding='utf-8-sig')

    for ota in otas:
        sub_dst = replace_all(metadata_schema, {'ota': ota})
        _dst = dst_path.joinpath(sub_dst)
        _dst.mkdir(parents=True, exist_ok=True)

        for metadata in metadatas:
            _meta = metadatas[metadata]
            _meta = ota_re.sub(f'\g<1>{ota}\g<3>', _meta)
            _meta = date_re.sub(f'\g<1>{date}\g<3>', _meta)

            _dst.joinpath(f"{metadata}.xml").write_text(_meta,
                                                        encoding='utf-8-sig')


# create_empty_shapes(src="C:\KT2-11\!InputData\Shapefiles\Empty_Shapefiles",
#                     dst="C:\KT2-11\!OutputData\ParadosiData",
#                     otas=ot,
#                     meleti_shapes=['ASTOTA', 'NOMI', 'OIK'],
#                     local_schema="<ota>/SHAPE/<shape>")
