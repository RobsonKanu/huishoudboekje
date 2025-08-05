
import os
import uuid
import pandas as pd

from datetime import date
from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State

from project_huishoudboekje.config import AppSettings
from project_huishoudboekje.database import (
    connect_to_database, read_sql_table_cats, files_in_budget, delete_files_from_budget,
    remove_category)
from project_huishoudboekje.utils.prep_data import (prepare_data, prepare_data_budget, parse_contents_file_import,
                                                    group_data_for_table)
from project_huishoudboekje.components.navbar import navbar
from project_huishoudboekje.pages.page_dashboard import layout as layout_dashboard
from project_huishoudboekje.pages.page_budget_actuals import layout as layout_budget_actuals
from project_huishoudboekje.pages.page_data import layout as layout_data
from project_huishoudboekje.pages.page_settings import layout as layout_settings

from project_huishoudboekje.config import GeneralSettings
from project_huishoudboekje.read_rabo import ReadRabo
from project_huishoudboekje.read_asn import ReadAsn
from project_huishoudboekje.find_category import FindCategory
from project_huishoudboekje.store_results import StoreResults

# List of months for table use
month_names = [f'{GeneralSettings.year_selected}-0' + str(i) for i in list(range(1, 10))] + [
    f'{GeneralSettings.year_selected}-' + str(i) for i in list(range(10, 13))]

# Load data transactions
df_data = pd.read_excel(GeneralSettings.project_path / 'data/processed/transactions.xlsx').sort_values(
    by='DATE', ascending=False)

# Filter data for selected year
df_data = df_data[(df_data['DATE'] >= f'{GeneralSettings.year_selected}-01-01') & (
        df_data['DATE'] < f'{GeneralSettings.year_selected + 1}-01-01')].copy(deep=True)

# Prepare data for analysis
df_analysis = prepare_data(df_data)

# Refactor date column
df_data.DATE = pd.DatetimeIndex(df_data.DATE).strftime("%Y-%m-%d")

# Load categories
df_categories = read_sql_table_cats(to_records=False, fill_nan_end_year=True).astype(
    {'begin_year': 'int', 'end_year': 'int'})

df_categories = df_categories[(df_categories.begin_year <= GeneralSettings.year_selected) & (
        df_categories.end_year >= GeneralSettings.year_selected)].drop(
    columns=['begin_year', 'end_year']).rename(columns={'grouplevel': 'group'})

df_categories.columns = df_categories.columns.str.upper()

df_budget = prepare_data_budget(df_analysis['DATE'].max(), GeneralSettings.year_selected)

# Initialize app
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=AppSettings().style_sheet)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


# Dashboard: table actuals and budget for selected group
@app.callback(Output('data-groups', 'data'),
              Output('data-groups-budget', 'data'),
              Input('dropdown-groups', 'value'))
def update_rows(selected_value):
    global df_analysis, df_budget, month_names

    df_pivot_actuals = group_data_for_table(df_analysis, selected_value, 'AMOUNT_NW', month_names)
    df_pivot_budget = group_data_for_table(df_budget, selected_value, 'BUDGET', month_names)

    return df_pivot_actuals, df_pivot_budget


@app.callback(Output('checklist-remove-files', 'options', allow_duplicate=True),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              prevent_initial_call=True)
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None:
        for contents, filename in zip(list_of_contents, list_of_names):
            parse_contents_file_import(contents, filename)

        lst_source_files = files_in_budget()

        return lst_source_files


# Modal settings: close modal that no file is selected
@app.callback(Output('modal-no-selection', 'is_open', allow_duplicate=True),
              Input('no-selection-close', 'n_clicks'),
              prevent_initial_call=True)
def close_no_selection(n_clicks):
    if n_clicks:
        return False


# Modal settings: no file selected to remove
@app.callback(Output('modal-remove-file', 'is_open', allow_duplicate=True),
              Input('no-remove-file', 'n_clicks'),
              prevent_initial_call=True)
def close_no_selection(n_clicks):
    if n_clicks:
        return False

@app.callback(Output('modal-remove-file', 'is_open', allow_duplicate=True),
              Output('checklist-remove-files', 'options', allow_duplicate=True),
              Output('checklist-remove-files', 'value'),
              Input('yes-remove-file', 'n_clicks'),
              State('checklist-remove-files', 'value'),
              prevent_initial_call=True)
def close_no_selection(n_clicks, selection):
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'yes-remove-file':
        src_files = delete_files_from_budget(selection)

        return False, src_files, []

@app.callback(Output('modal-remove-file', 'is_open'),
              Output('modal-no-selection', 'is_open'),
              Input('remove-files', 'n_clicks'),
              State('checklist-remove-files', 'value'))
def open_modal_remove_files(n_clicks, val):
    if n_clicks and val:
        return True, False

    if n_clicks and not val:
        return False, True

    return False, False

@app.callback(Output('modal-remove', 'is_open', allow_duplicate=True),
              Output('table-category', 'data', allow_duplicate=True),
              Input('yes-remove', 'n_clicks'),
              Input('no-remove', 'n_clicks'),
              State('table-category', 'active_cell'),
              State('table-category', 'data'),
              prevent_initial_call=True
              )
def toggle_remove_row(ny, nn, active_cell, data):
    row = data[active_cell['row']]

    if nn:
        df_cats = read_sql_table_cats()
        return False, df_cats
    if ny:
        remove_category(row)

        df_cats = read_sql_table_cats()

        return False, df_cats

@app.callback(Output('modal-edit', 'is_open'),
              Output('modal-remove', 'is_open'),
              Output('group-edit', 'value'),
              Output('category-edit', 'value'),
              Output('startyear-edit', 'value'),
              Output('endyear-edit', 'value'),
              Input('table-category', 'active_cell'),
              State('table-category', 'data')
              )
def open_modal_cell(active_cell, data):

    if not active_cell:
        return False, False, None, None, None, None

    row = data[active_cell['row']]

    if active_cell['column'] == 4:
        return True, False, row['grouplevel'], row['category'], row['begin_year'], row['end_year']
    elif active_cell['column'] == 5:
        return False, True, None, None, None, None
    else:
        return False, False, None, None, None, None

@app.callback(Output('modal-edit', 'is_open', allow_duplicate=True),
              Output('table-category', 'data', allow_duplicate=True),
              Input('close-edit', 'n_clicks'),
              Input('submit-cat-edit', 'n_clicks'),
              State('group-edit', 'value'),
              State('category-edit', 'value'),
              State('startyear-edit', 'value'),
              State('endyear-edit', 'value'),
              State('table-category', 'active_cell'),
              State('table-category', 'data'),
              prevent_initial_call=True)
def handle_modal_edit(n1, n2, group, cat, sy, ey, active_cell, data):
    if ctx.triggered_id == 'close-edit':
        df_cats = read_sql_table_cats()
        return False, df_cats
    else:
        row = data[active_cell['row']]
        cursor, conn = connect_to_database()

        sql_remove = f"""DELETE FROM categories WHERE id=?;"""

        cursor.execute(sql_remove, (f'{row['grouplevel']}_{row['category']}_{row['begin_year']}',))
        conn.commit()

        params = (f'{group}_{cat}_{sy}', group, cat, sy, ey)

        sql_row = f"""INSERT INTO categories VALUES (?, ?, ?, ?, ?);"""

        cursor.execute(sql_row, params)
        conn.commit()

        df_cats = read_sql_table_cats()

        cursor.close()
        conn.close()

        return False, df_cats

@app.callback(
     Output("modal", "is_open"),
     Output('table-category', 'data'),
     Input("open", "n_clicks"),
     Input("close", "n_clicks"),
     Input('submit-cat', 'n_clicks'),
     State("modal", "is_open"),
     State('group', 'value'),
     State('category', 'value'),
     State('startyear', 'value'),
     State('endyear', 'value'),
)
def toggle_modal(n1, n2, n3, is_open, group, cat, startyear, endyear):

    df_cats = read_sql_table_cats()

    if not ctx.triggered_id:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered_id

    if button_id == 'submit-cat':
        print('Connect to database...')
        cursor, conn = connect_to_database()

        # todo: check input

        params = (f'{group}_{cat}_{startyear}', group, cat, startyear, endyear)

        sql_row = f"""INSERT INTO categories VALUES (?, ?, ?, ?, ?);"""

        cursor.execute(sql_row, params)

        conn.commit()

        df_cats = read_sql_table_cats()

        cursor.close()
        conn.close()

        return not is_open, df_cats

    if button_id == 'open' or button_id == 'close':
        return not is_open, df_cats

    return is_open, df_cats

@app.callback(Output('data-view', 'data'),
              [Input('dropdown-view', 'value')])
def create_table_output(view_value):

    df = pd.read_excel(GeneralSettings.project_path / 'data/processed/transactions.xlsx').sort_values(
        by='DATE', ascending=False)

    df = df[df.GROUP != 'Inkomsten']

    df_budget = pd.read_excel(GeneralSettings.project_path / f'data/budget{GeneralSettings.year_selected}.xlsx')
    df_budget['DATE'] = pd.to_datetime(df_budget['YEAR_MONTH'], format='%Y-%m')
    df_budget = df_budget[df_budget.GROUP != 'Inkomsten']

    df_analysis = prepare_data(df)

    if view_value == 'YTD':
        ref_date = date.today().replace(day=1)

        df_analysis = df_analysis[df_analysis['DATE'] < ref_date.strftime('%Y-%m-%d')]
        df_budget = df_budget[df_budget['DATE'] < ref_date.strftime('%Y-%m-%d')]

    df_analysis_tot = df_analysis.groupby('CATEGORY')['AMOUNT_NW'].sum()
    df_budget_tot = df_budget.groupby('CATEGORY')['BUDGET'].sum()

    df_tot = pd.concat([df_budget_tot, df_analysis_tot], axis=1).fillna(0).sort_values(
        by='AMOUNT_NW', ascending=False)

    df_tot.loc['Total'] = df_tot.sum()

    df_tot['DELTA'] = df_tot['BUDGET'] - df_tot['AMOUNT_NW']
    df_tot['RATIO'] = df_tot['AMOUNT_NW'] / df_tot['BUDGET']

    return df_tot.reset_index().round(2).to_dict('records')

@app.callback(
    Output('page-2-content', 'data'),
    Output('editing-rows-button', 'n_clicks'),
    Input('editing-rows-button', 'n_clicks'),
    State('page-2-content', 'data'),
    State('page-2-content', 'columns'),
    State('page-2-content', 'active_cell'),
    State('page-2-content', 'page_current'))
def add_row(n_clicks, rows, columns, active_cell, page_num):
    if n_clicks > 0:

        if active_cell:
            row_insert = active_cell['row'] + page_num * 15 + 1
        else:
            row_insert = 0

        rows.insert(row_insert, {c['id']: '' for c in columns})

        n_clicks = 0

    return rows, n_clicks

@app.callback(
    Output('modal-duplicate-trans', 'is_open', allow_duplicate=True),
    Output('data-duplicates', 'data'),
    Input('duplicate-trans-button', 'n_clicks'),
    State("page-2-content", "data"),
    prevent_initial_call=True
)
def show_duplicates(n_clicks, table):
    if n_clicks > 0:

        df_dup = pd.DataFrame(table)[['DATE', 'PARTY', 'AMOUNT']]

        return True, df_dup[df_dup.duplicated()].to_dict('records')
    else:
        return False, None

@app.callback(
    Output('modal-duplicate-trans', 'is_open', allow_duplicate=True),
    Input('close-modal-duplicate-trans', 'n_clicks'),
    prevent_initial_call=True
)
def close_modal_duplicate_trans(n_clicks):
    if n_clicks > 0:
        return False
    else:
        return True


@app.callback(
    Output("output-1", "children"),
    Input("save-button", "n_clicks"),
    State("page-2-content", "data"))
def selected_data_to_csv(nclicks, table1):
    if nclicks > 0:
        df_out = pd.DataFrame(table1)
        df_out['DATE'] = pd.to_datetime(df_out['DATE'], format='%Y-%m-%d')
        df_out['TRANS_ID'] = df_out['TRANS_ID'].apply(lambda x: uuid.uuid4() if x == '' else x)
        df_out['TRANSACTION_TYPE'] = df_out['TRANSACTION_TYPE'].apply(lambda x: '-' if x == '' else x)

        df_out = df_out.drop('GROUP', axis=1).merge(
            df_categories, how='left', left_on='CATEGORY', right_on='CATEGORY')

        df_out.to_excel(GeneralSettings.project_path / 'data/processed/transactions.xlsx', index=False)
        return "Data Submitted"


# Update the index
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/dashboard':
        return layout_dashboard.create_layout(navbar, df_analysis, month_names)
    elif pathname == '/data':
        return layout_data.create_layout(navbar, df_data, df_categories)
    elif pathname == '/budget':
        return layout_budget_actuals.create_layout(navbar, df_budget, df_analysis)
    elif pathname == '/settings':
        return layout_settings.create_layout(navbar)
    else:
        return layout_dashboard.create_layout(navbar, df_analysis, month_names)


def run():
    filenames_rabobank = next(os.walk(GeneralSettings.project_path / f'data/Rabobank'), (None, None, []))[2]
    filenames_asn_bank = next(os.walk(GeneralSettings.project_path / f'data/ASN Bank'), (None, None, []))[2]

    if filenames_rabobank:
        df_rabo = ReadRabo().run(filenames_rabobank)
        df_rabo = FindCategory().run(df_rabo, 'Rabobank')
        StoreResults().run(df_rabo)

    if filenames_asn_bank:
        df_asn = ReadAsn().run(filenames_asn_bank)
        df_asn = FindCategory().run(df_asn, 'ASN Bank')
        StoreResults().run(df_asn)

    app.run_server(debug=True)


if __name__ == '__main__':
    run()
