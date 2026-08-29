
import sqlite3
import pandas as pd

from contextlib import contextmanager
from datetime import datetime

from project_huishoudboekje.config import DatabaseSettings, GeneralSettings

# Track whether the schema (CREATE TABLE IF NOT EXISTS ...) has already been ensured
# for this process, so we don't re-run it on every single query.
_schema_ready = False

# Table names are interpolated based on `test_par` (either '' or '_test'). Interpolating
# arbitrary strings into SQL identifiers is unsafe, so we resolve through this whitelist
# instead of using the raw value directly in an f-string.
_TRANSACTIONS_TABLES = {
    '': 'transactions',
    '_test': 'transactions_test',
}


def _transactions_table_name(test_par):
    try:
        return _TRANSACTIONS_TABLES[test_par]
    except KeyError:
        raise ValueError(
            f"Unknown test_par={test_par!r}; expected one of {list(_TRANSACTIONS_TABLES)}")


@contextmanager
def db_connection():
    """Context manager yielding (cursor, conn) for the sqlite database.

    Ensures the schema exists (once per process) and always closes the cursor/connection,
    even if an exception is raised inside the `with` block. Raises rather than silently
    swallowing connection errors, so callers don't get a confusing crash further downstream.
    """
    global _schema_ready

    conn = sqlite3.connect(GeneralSettings.project_path / 'data' / DatabaseSettings.database_name)

    try:
        cursor = conn.cursor()

        if not _schema_ready:
            for statement in DatabaseSettings.sql_statements:
                cursor.execute(statement)
            conn.commit()
            _schema_ready = True

        yield cursor, conn
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Failed to access database: {e}") from e
    finally:
        conn.close()


def connect_to_database():
    """Deprecated: kept temporarily for backwards compatibility.

    Prefer `with db_connection() as (cursor, conn):` instead, which closes the connection
    automatically. This function is no longer used elsewhere in this module.
    """
    global _schema_ready

    conn = sqlite3.connect(GeneralSettings.project_path / 'data' / DatabaseSettings.database_name)
    cursor = conn.cursor()

    if not _schema_ready:
        for statement in DatabaseSettings.sql_statements:
            cursor.execute(statement)
        conn.commit()
        _schema_ready = True

    return cursor, conn


def read_sql_table_cats(to_records=True, fill_nan_end_year=False, add_edit_emoji=False, add_remove_emoji=False):
    with db_connection() as (cursor, conn):
        df = pd.read_sql("""SELECT * FROM categories""", conn)

    if add_edit_emoji:
        df['edit'] = '✏️'

    if add_remove_emoji:
        df['remove'] = '❌'

    if fill_nan_end_year:
        df['end_year'] = df['end_year'].fillna('9999').astype(str).replace('', '9999').replace('None', '9999').astype('int')

    if to_records:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year']).to_dict('records')
    else:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year'])


def read_sql_table_budget(year=None, keep_src=False):
    with db_connection() as (cursor, conn):
        df = pd.read_sql("""SELECT * FROM budget""", conn)

    if year:
        df = df[df.year_month.str.startswith(str(year))].copy()

    cols_exclude = ['id'] if keep_src else ['id', 'source_file']

    return df.drop(columns=cols_exclude).rename(columns={
        'grouplevel': 'GROUP', 'category': 'CATEGORY', 'year_month': 'YEAR_MONTH', 'amount': 'BUDGET'})


def files_in_budget():
    with db_connection() as (cursor, conn):
        df = pd.read_sql("""SELECT distinct(source_file) FROM budget order by source_file""", conn)

    return df.iloc[:, 0].to_list()


def delete_files_from_budget(selection):
    with db_connection() as (cursor, conn):
        for sel in selection:
            cursor.execute("""DELETE FROM budget where source_file = ?""", (sel,))

        conn.commit()

        df = pd.read_sql("""SELECT distinct(source_file) FROM budget order by source_file""", conn)

    return df.iloc[:, 0].to_list()


def remove_category(row):
    with db_connection() as (cursor, conn):
        sql_remove = """DELETE FROM categories WHERE id=?;"""

        cursor.execute(sql_remove, (f"{row['grouplevel']}_{row['category']}_{row['begin_year']}",))
        conn.commit()


def add_category(params):
    with db_connection() as (cursor, conn):
        sql_add = """INSERT INTO categories VALUES (?, ?, ?, ?, ?);"""

        cursor.execute(sql_add, params)
        conn.commit()


def add_budget_file_to_db(df, filename):
    with db_connection() as (cursor, conn):
        df['id'] = df['GROUP'] + '_' + df['CATEGORY'] + '_' + df['YEAR_MONTH']
        df['source_file'] = filename

        df[['id', 'GROUP', 'CATEGORY', 'YEAR_MONTH', 'BUDGET', 'source_file']].rename(
            columns={'GROUP': 'grouplevel',
                     'CATEGORY': 'category',
                     'YEAR_MONTH': 'year_month',
                     'BUDGET': 'amount'}).to_sql(name='budget',
                                                 con=conn,
                                                 if_exists='append',
                                                 index=False)

        conn.commit()


def add_transactions_to_db(df, test_par=""):
    table_name = _transactions_table_name(test_par)

    with db_connection() as (cursor, conn):
        df['TS_CHANGED'] = datetime.now().timestamp()

        df.rename(columns={'GROUP': 'GROUPLEVEL'}).astype({'TRANS_ID': 'str'}).to_sql(
            name=table_name,
            con=conn,
            if_exists='append',
            index=False)

        conn.commit()


def read_sql_table_transactions(year=None, test_par=""):
    table_name = _transactions_table_name(test_par)

    with db_connection() as (cursor, conn):
        df = pd.read_sql(f"""
            SELECT * FROM (
                SELECT *, ROW_NUMBER() OVER(PARTITION BY TRANS_ID ORDER BY TS_CHANGED DESC) 
                AS rn FROM {table_name}) AS a
            WHERE rn = 1 
        """, conn)

    if year:
        df = df[df.DATE.str.startswith(str(year))].copy()

    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M:%S')

    return df.drop(columns=['rn']).rename(columns={'GROUPLEVEL': 'GROUP'})
