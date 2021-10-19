# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Union
from atktima.path import paths
from at.sql.utils import load_app_queries
from at.sql.object import QueryObject
from at.sql.sqlite import SQLiteEngine
from at.state import State
from at.utils import user

init_sql_queries = load_app_queries(paths.get_init_sql())
app_queries = load_app_queries(paths.get_sql())


class KtimaSQL(SQLiteEngine):
    def __init__(self,
                 db: Union[str, Path],
                 app_paths: Union[List[QueryObject], None] = None) -> None:
        super().__init__(db=db, app_paths=app_paths)

    def load_state(self):
        user_settings = self.get_user_settings()
        meletes = self.get_meleti_ota_info()
        all_mel_codes = {'all_mel_codes': meletes.keys()}

        initial_db_state = {**user_settings, **meletes, **all_mel_codes}

        return initial_db_state

    def save_state(self, state: State):
        settings = app_queries['update_user_settings']
        params = state.get(values_only=True)

        self.update(settings.set(**params))

    def get_user_settings(self) -> dict:
        username = user()
        query = app_queries['select_user_settings'].attrs(fetch='row',
                                                          colname=True).set(username=username)
        result = self.select(query)
        if result is not None:
            user_settings = dict(zip(result[0], result[1]))
            return user_settings
        else:
            self.insert(app_queries['insert_user'].set(username=username))
            return self.get_user_settings()

    def get_meleti_ota_info(self):
        meletes = {}
        query = app_queries['select_meletes'].attrs(fetch='rows')
        meleti_code_name = db.select(query)

        query = app_queries['select_all_companies'].attrs(fetch='col')
        companies = db.select(query)

        for meleti_code, meleti_name in meleti_code_name:
            meletes[meleti_code] = {'name': meleti_name, 'company': {}}
            for company in companies:
                query = app_queries['select_ota_from_meleti_company'].attrs(
                    fetch='col').set(meleti=meleti_code, company=company)
                meleti_company_ota = db.select(query)

                if meleti_company_ota:
                    meletes[meleti_code]['company'][company] = meleti_company_ota

        return meletes

    def get_shapes(self, meleti: str, stype='ktima'):
        query = app_queries['select_shapes'].attrs(
            fetch='col').set(meleti=meleti, type=stype)
        result = self.select(query)

        return result


db = KtimaSQL(db=paths.get_db(), app_paths=paths)

# print(db.select(app_queries['select_meletes'].attrs(fetch='multirow')))
# print(db.select(app_queries['select_all_companies'].attrs(fetch='singlecol')))
# print(db.select(app_queries['select_ota_from_meleti_company'].attrs(
#     fetch='singlecol').set(meleti="KT2-11", company="NAMA")))

# print(db.get_user_settings())
