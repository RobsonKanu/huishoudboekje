
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

            print("Tables created successfully.")

            return cursor, conn

    except sqlite3.OperationalError as e:
        print("Failed to open database:", e)


def read_sql_table_cats(to_records=True, fill_nan_end_year=False):
    cursor, conn = connect_to_database()

    df = pd.read_sql("""SELECT * FROM categories""", conn)

    cursor.close()
    conn.close()

    if fill_nan_end_year:
        df['end_year'] = df['end_year'].str.replace('', '9999').fillna('9999')

    if to_records:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year']).to_dict('records')
    else:
        return df.drop(columns=['id']).sort_values(by=['grouplevel', 'category', 'begin_year'])


def read_sql_table_budget():

    cursor, conn = connect_to_database()

    df = pd.read_sql("""SELECT * FROM budget""", conn)

    cursor.close()
    conn.close()

    return df.drop(columns=['id', 'source_file']).rename(columns={
        'grouplevel': 'GROUP', 'category': 'CATEGORY', 'year_month': 'YEAR_MONTH', 'amount': 'BUDGET'})

