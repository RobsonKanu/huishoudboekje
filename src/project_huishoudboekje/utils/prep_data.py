import io
import base64
import pandas as pd

from dash import html

from project_huishoudboekje.config import GeneralSettings
from project_huishoudboekje.database import read_sql_table_budget, add_budget_file_to_db


def prepare_data(df):
    # Filter data for analysis indicator
    df_analysis = df.loc[df.ANALYSE_IND == 1].copy(deep=True)

    # Create year-month column
    df_analysis['YEAR_MONTH'] = pd.DatetimeIndex(df_analysis.DATE).strftime("%Y-%m")

    # Create new amount column
    df_analysis['AMOUNT_NW'] = df_analysis.apply(
        lambda x: -x['AMOUNT'] if ((x['FINANCIAL_TYPE'] == 'credit') & (x['GROUP'] != 'Inkomsten')) | (
                (x['FINANCIAL_TYPE'] == 'debet') & (x['GROUP'] == 'Inkomsten')) else x['AMOUNT'], axis=1)

    # Create income indicator
    df_analysis['INCOME_IND'] = df['GROUP'].apply(lambda x: x if x == 'Inkomsten' else 'Uitgaven')

    return df_analysis


def prepare_data_budget(ref_date, sel_year):

    # df = pd.read_excel(GeneralSettings.project_path / f'data/budget{sel_year}.xlsx')
    df = read_sql_table_budget(year=GeneralSettings.year_selected)
    df['DATE'] = pd.to_datetime(df['YEAR_MONTH'], format='%Y-%m')

    df['AMOUNT_NW'] = df.apply(lambda x: x['BUDGET'] if x['GROUP'] == 'Inkomsten' else x['BUDGET'], axis=1)

    df['INCOME_IND'] = df['GROUP'].apply(lambda x: x if x == 'Inkomsten' else 'Uitgaven')

    return df[(df.DATE >= pd.to_datetime(f'{GeneralSettings.year_selected}-01-01')) & (
            df.DATE <= ref_date)].copy(deep=True)


def parse_contents_file_import(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)

    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        df = pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xlsx' in filename:
        # Assume that the user uploaded an excel file
        df = pd.read_excel(io.BytesIO(decoded))
    else:
        raise ValueError(f'Unable to parse contents of file={filename}')

    # todo: open modal if file already exists 'message first remove file before importing again'
    add_budget_file_to_db(df, filename)


def group_data_for_table(df, selected_value, values_col, month_names):
    df_sel = pd.pivot_table(df[df.GROUP == selected_value], values=values_col,
                                       index=['CATEGORY'], columns=['YEAR_MONTH'], aggfunc='sum').reset_index()

    for col in set(month_names) - set(df_sel.columns):
        df_sel[col] = 0.0

    df_sel['Total'] = df_sel[month_names].sum(axis=1)
    df_sel = df_sel.fillna(0).sort_values(by=['CATEGORY'], ascending=True)
    df_sel.loc['Total'] = df_sel.sum()
    df_sel.loc['Total', 'CATEGORY'] = 'Total'

    return df_sel.round(2).to_dict('records')
