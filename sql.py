# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Union
from atktima.path import paths
from at.sql.utils import load_app_queries
from at.sql.object import QueryObject
from at.sql.sqlite import SQLiteEngine
from at.state import State

init_sql_queries = load_app_queries(paths.get_init_sql())
app_queries = load_app_queries(paths.get_sql())


class KtimaSQL(SQLiteEngine):
    def __init__(self,
                 db: Union[str, Path],
                 app_paths: Union[List[QueryObject], None] = None) -> None:
        super().__init__(db=db, app_paths=app_paths)

    def load_state(self):
        query = app_queries['select_user_settings'].attrs(fetch='singlerow',
                                                          cols=True)
        settings_result = self.select(query)
        user_settings = dict(zip(settings_result[0], settings_result[1]))

        query = app_queries['select_meletes'].attrs(fetch='multirow')
        meletes_result = self.select(query)
        meletes = dict(meletes_result)
        all_meletes = {'meletes': meletes.keys()}

        initial_db_state = {**user_settings, **meletes, **all_meletes}

        return initial_db_state

    def save_state(self, state: State):
        settings = app_queries['update_user_settings']
        params = state.get(values_only=True)

        self.update(settings.set(**params))


db = KtimaSQL(db=paths.get_db(), app_paths=paths)
