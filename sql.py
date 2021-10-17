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
        settings = app_queries['select_user_settings'].attrs(fetch='singlerow',
                                                             cols=True)
        result = self.select(settings)

        return dict(zip(result[0], result[1]))

    def save_state(self, state: State):
        settings = app_queries['update_user_settings']
        params = state.get(values_only=True)

        self.update(settings.set(**params))


db = KtimaSQL(db=paths.get_db(), app_paths=paths)
state = State.from_db(db)
print(state.get())
print(state['fullname'])
print(state['meleti'])
state.set({'meleti': 'KT5-14', 'kthmatemp': 'T:/'})
# state['meleti'] = "KT5-16"
# state['username'] = 'aznavouridis.k'
print(state['meleti'])
