
import os

from datetime import datetime
from pathlib import Path
from dash.dash_table.Format import Format, Group, Symbol, Scheme

import dash_bootstrap_components as dbc


class GeneralSettings(object):

    # Override with the HUISHOUDBOEKJE_DATA_PATH environment variable so the code doesn't
    # need to be edited per machine/user. Falls back to the original hardcoded path.
    project_path = Path(os.environ.get(
        'HUISHOUDBOEKJE_DATA_PATH', r'C:\Users\robsc\Documents\Analyse\Huishoudboekje'))

    # Override with HUISHOUDBOEKJE_YEAR to look at a different year; defaults to the current
    # year so this no longer needs a manual edit every January.
    year_selected = int(os.environ.get('HUISHOUDBOEKJE_YEAR', datetime.now().year))

    test_par = ''  # use '_test' for test and '' for production
    debug = False


class AppSettings(object):

    style_sheet = [dbc.themes.UNITED]


class TableSettings(object):

    euro_format = Format(precision=2,
                         group=Group.yes,
                         groups=3,
                         group_delimiter=" ",
                         scheme=Scheme.fixed,
                         symbol=Symbol.yes,
                         symbol_prefix=u'€ '
                         )


class FigureSettings(object):

    group_colors = {
        'Aankopen': '#636EFA',
        'Auto en vervoer': '#EF553B',
        'Giften': '#00CC96',
        'Leven en entertainment': '#AB63FA',
        'Overig': '#FFA15A',
        'Verzekeringen': '#19D3F3',
        'Verzorging en gezondheid': '#FF6692',
        # 'Woning': '#B6E880',
        'Woonlasten': '#B6E880'
    }


class DatabaseSettings:
    database_name = 'huishoudboekje.db'

    sql_statements = [
        """CREATE TABLE IF NOT EXISTS categories (
                id text PRIMARY KEY, 
                grouplevel text NOT NULL, 
                category text NOT NULL,
                begin_year INT, 
                end_year INT
            );""",
        """CREATE TABLE IF NOT EXISTS budget (
                id text PRIMARY KEY,
                grouplevel text NOT NULL,
                category text NOT NULL,
                year_month text NOT NULL,
                amount real NOT NULL,
                source_file text NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS transactions (
                TRANS_ID text,
                DATE text,
                SOURCE text,
                TRANSACTION_TYPE text,
                FINANCIAL_TYPE text,
                PARTY text,
                AMOUNT real,
                GROUPLEVEL text,
                CATEGORY text,
                ANALYSE_IND int,
                TS_CHANGED real
        )
        """,
        """CREATE TABLE IF NOT EXISTS transactions_test (
                        TRANS_ID text,
                        DATE text,
                        SOURCE text,
                        TRANSACTION_TYPE text,
                        FINANCIAL_TYPE text,
                        PARTY text,
                        AMOUNT real,
                        GROUPLEVEL text,
                        CATEGORY text,
                        ANALYSE_IND int,
                        TS_CHANGED real
        )
        """
    ]
