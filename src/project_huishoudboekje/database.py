
import sqlite3
import pandas as pd

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


def read_sql_table_cats(to_records=True, fill_nan_end_year=False):
    cursor, conn = connect_to_database()

    df = pd.read_sql("""SELECT * FROM categories""", conn)

    cursor.close()
    conn.close()

    if fill_nan_end_year:
        df['end_year'] = df['end_year'].astype(str).replace('', '9999').replace('None', '9999').astype('int')

    if to_records:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year']).to_dict('records')
    else:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year'])


def read_sql_table_budget(year=None):

    cursor, conn = connect_to_database()

    df = pd.read_sql("""SELECT * FROM budget""", conn)

    if year:
        df = df[df.year_month.str.startswith(str(year))].copy()

    cursor.close()
    conn.close()

    return df.drop(columns=['id', 'source_file']).rename(columns={
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
