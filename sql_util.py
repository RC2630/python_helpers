import pymysql
from pymysql.connections import Connection
from pymysql.cursors import Cursor
from typing import Any, Callable
import pandas as pd

type Row = tuple[Any, ...]
type Table = tuple[Row, ...]

# -----------------------------------------------------

def run_sql_query(query: str, **connection_config: str) -> Table:

    conn: Connection = pymysql.connect(
        host = connection_config.get("host", "localhost"),
        user = connection_config.get("user", "root"),
        password = connection_config.get("password", "Future2630!"),
        database = connection_config.get("database", "misc"),
        cursorclass = Cursor
    )

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        conn.close()

# -----------------------------------------------------

def sql_to_pandas(
    table_name: str | None = None, query: str | None = None,
    columns: list[str] | None = None, **connection_config: str
) -> pd.DataFrame:
    
    if (columns is None or query is None) and table_name is None:
        raise ValueError("table_name must be specified if columns or query is None")
    
    if columns is None:
        column_info: Table = run_sql_query(
            f"select column_name from information_schema.columns "
            f"where table_name = '{table_name}' "
            f"and table_schema = '{connection_config.get("database", "misc")}' "
            f"order by ordinal_position",
            **connection_config
        )
        columns = [entry[0] for entry in column_info]
    assert columns is not None

    if query is None:
        query = f"select * from {table_name}"
    assert query is not None
    data: Table = run_sql_query(query, **connection_config)

    return pd.DataFrame(data, columns = columns)

# -----------------------------------------------------

class SqlQuery:

    def __init__(
        self, query: str | None = None,
        table_name: str | None = None, columns: list[str] | None = None
    ) -> None:
        self.query: str = query if query is not None else ""
        self.table_name: str | None = table_name
        self.columns: list[str] | None = columns.copy() if columns is not None else None

    def __getattr__(self, name: str) -> Callable[[Any], SqlQuery]:
        name = name.replace("_", " ").upper()
        def add_to_query_(add2: Any = None) -> SqlQuery:
            new_query = SqlQuery(self.query, self.table_name, self.columns)
            new_query.add_to_query(name, add2)
            return new_query
        return add_to_query_
        
    @staticmethod
    def get_canonical(column: str) -> str:
        column = column.strip()
        column = column.replace(" as ", " AS ").replace(" As ", " AS ").replace(" aS ", " AS ")
        if " AS " in column:
            return column.split(" AS ")[-1].strip()
        else:
            return column

    def add_to_query(self, add1: str, add2: Any = None) -> None:
        if self.query != "":
            self.query += " "
        self.query += add1
        if add2 is not None:
            if isinstance(add2, SqlQuery):
                add2 = f"({add2.query})"
            self.query += " " + str(add2)
        if add1 == "FROM" and self.table_name is None:
            self.table_name = str(add2).strip().split()[0]
        if add1 == "SELECT" and self.columns is None and str(add2).lower().strip() not in ["*", "distinct *"]:
            self.columns = [SqlQuery.get_canonical(column) for column in str(add2).split(",")]

    def get_query_string(self) -> str:
        return self.query
    
    def __str__(self) -> str:
        return self.query
    
    def __repr__(self) -> str:
        return self.query
    
    def run(self, **connection_config: str) -> Table:
        return run_sql_query(self.query, **connection_config)
    
    def run_to_pandas(
        self, table_name: str | None = None,
        columns: list[str] | None = None, **connection_config: str
    ) -> pd.DataFrame:
        if table_name is None and columns is None:
            if self.columns is not None:
                columns = self.columns.copy()
            elif self.table_name is not None:
                table_name = self.table_name
            else:
                raise ValueError("automatic inference of columns and/or table name failed")
        return sql_to_pandas(table_name, self.query, columns, **connection_config)