# -*- coding: utf-8 -*-


from typing import Union
from pathlib import Path
from at.io.copyfuncs import copy_file
from at.result import Result


def create_mel_folder(template_folder: Union[str, Path], meleti: str):
    src_path = Path(template_folder)
    dst_path = Path("C:/")

    if dst_path.joinpath(meleti).exists():
        return Result.warning('Ο φάκελος της μελέτης υπάρχει ήδη')

    basic_schema = src_path.joinpath('Folder_Structure')
    mel_spesifics = src_path.joinpath(f'File_Structure/{meleti}')
    copy_file(basic_schema, dst_path, save_name=meleti, ignore=['*.ini'])
    copy_file(mel_spesifics, dst_path, save_name=meleti, ignore=['*.ini'])

    out_folder = dst_path.joinpath(meleti)

    if out_folder.exists():
        return Result.success("Ο φάκελος της μελέτης δημιουργήθηκε",
                              details={'secondary': str(out_folder)})
    else:
        return Result.error("Αποτυχία κατά τη δημιουργία φακέλου μελέτης")
