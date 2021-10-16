# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List, Union
from atktima.path import paths
from at.sql.query import QueryObject, load_create_queries, load_sql_queries
from at.sql.sqlite import SQLiteEngine

create_sql_queries = load_create_queries(paths.get_create_folder())
sql_queries = load_sql_queries(paths.get_static())


class KtimaSQL(SQLiteEngine):
    def __init__(self,
                 db: Union[str, Path],
                 create_queries: Union[List[QueryObject], None] = None) -> None:
        super().__init__(db=db, create_queries=create_queries)


db = KtimaSQL(db=paths.get_db(), create_queries=create_sql_queries)
