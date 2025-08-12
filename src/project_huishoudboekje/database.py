
import sqlite3
import pandas as pd

from datetime import datetime

from project_huishoudboekje.config import DatabaseSettings, GeneralSettings


def connect_to_database():
    try:
        with sqlite3.connect(GeneralSettings.project_path / 'data' / DatabaseSettings.database_name) as conn:
            # interact with database

            cursor = conn.cursor()

            # execute statements
            for statement in DatabaseSettings.sql_statements:
                cursor.execute(statement)

            # commit the changes
            conn.commit()

            return cursor, conn

    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)


def read_sql_table_cats(to_records=True, fill_nan_end_year=False, add_edit_emoji=False, add_remove_emoji=False):
    cursor, conn = connect_to_database()

    df = pd.read_sql("""SELECT * FROM categories""", conn)

    cursor.close()
    conn.close()

    if add_edit_emoji:
        df['edit'] = '✏️'

    if add_remove_emoji:
        df['remove'] = '❌'

    if fill_nan_end_year:
        df['end_year'] = df['end_year'].astype(str).replace('', '9999').replace('None', '9999').astype('int')

    if to_records:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year']).to_dict('records')
    else:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year'])


def read_sql_table_budget(year=None, keep_src=False):

    cursor, conn = connect_to_database()

    df = pd.read_sql("""SELECT * FROM budget""", conn)

    if year:
        df = df[df.year_month.str.startswith(str(year))].copy()

    cursor.close()
    conn.close()

    cols_exclude = ['id'] if keep_src else ['id', 'source_file']

    return df.drop(columns=cols_exclude).rename(columns={
        'grouplevel': 'GROUP', 'category': 'CATEGORY', 'year_month': 'YEAR_MONTH', 'amount': 'BUDGET'})


def files_in_budget():

    cursor, conn = connect_to_database()

    df = pd.read_sql("""SELECT distinct(source_file) FROM budget""", conn)

    cursor.close()
    conn.close()

    return df.iloc[:, 0].to_list()


def delete_files_from_budget(selection):
    cursor, conn = connect_to_database()

    for sel in selection:
        cursor.execute("""DELETE FROM budget where source_file = ?""", (sel,))

    conn.commit()

    df_budget_sources = pd.read_sql("""SELECT * FROM budget""", conn)

    cursor.close()
    conn.close()

    return df_budget_sources.source_file.unique()


def remove_category(row):
    cursor, conn = connect_to_database()

    sql_remove = f"""DELETE FROM categories WHERE id=?;"""

    cursor.execute(sql_remove, (f'{row['grouplevel']}_{row['category']}_{row['begin_year']}',))
    conn.commit()

    cursor.close()
    conn.close()


def add_category(params):
    cursor, conn = connect_to_database()

    sql_add = f"""INSERT INTO categories VALUES (?, ?, ?, ?, ?);"""

    cursor.execute(sql_add, params)
    conn.commit()

    cursor.close()
    conn.close()


def add_budget_file_to_db(df, filename):
    cursor, conn = connect_to_database()

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
    cursor.close()
    conn.close()


def add_transactions_to_db(df, test_par=""):

    cursor, conn = connect_to_database()

    df['TS_CHANGED'] = datetime.now().timestamp()

    df.rename(columns={'GROUP': 'GROUPLEVEL'}).astype({'TRANS_ID': 'str'}).to_sql(name=f'transactions{test_par}',
                                                                                  con=conn,
                                                                                  if_exists='append',
                                                                                  index=False)

    conn.commit()
    cursor.close()
    conn.close()


def read_sql_table_transactions(year=None, test_par=""):

    cursor, conn = connect_to_database()

    df = pd.read_sql(f"""
        SELECT * FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY TRANS_ID ORDER BY TS_CHANGED DESC) 
            AS rn FROM transactions{test_par}) AS a
        WHERE rn = 1 
    """, conn)

    if year:
        df = df[df.DATE.str.startswith(str(year))].copy()

    cursor.close()
    conn.close()

    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y-%m-%d %H:%M:%S')

    return df.drop(columns=['rn']).rename(columns={'GROUPLEVEL': 'GROUP'})
