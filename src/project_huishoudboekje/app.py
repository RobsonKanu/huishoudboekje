
import os
import uuid
import pandas as pd

from dash import Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State

from project_huishoudboekje.config import AppSettings
from project_huishoudboekje.database import (
    read_sql_table_cats, files_in_budget, delete_files_from_budget,
    remove_category, add_category, add_transactions_to_db, read_sql_table_transactions)
from project_huishoudboekje.utils.prep_data import (prepare_data, prepare_data_budget, parse_contents_file_import,
                                                    group_data_for_table)
from project_huishoudboekje.components.navbar import navbar
from project_huishoudboekje.pages.page_dashboard import layout as layout_dashboard
from project_huishoudboekje.pages.page_budget_actuals import layout as layout_budget_actuals
from project_huishoudboekje.pages.page_data import layout as layout_data
from project_huishoudboekje.pages.page_settings import layout as layout_settings
from project_huishoudboekje.utils.general_components import get_label_style

from project_huishoudboekje.config import GeneralSettings as GenSet
from project_huishoudboekje.read_rabo import ReadRabo
from project_huishoudboekje.read_asn import ReadAsn
from project_huishoudboekje.find_category import FindCategory

# List of months for table use
month_names = [f'{GenSet.year_selected}-0' + str(i) for i in list(range(1, 10))] + [
    f'{GenSet.year_selected}-' + str(i) for i in list(range(10, 13))]

# Load data transactions
df_data = read_sql_table_transactions(year=GenSet.year_selected, test_par=GenSet.test_par).sort_values(
    by='DATE', ascending=False)

# Prepare data for analysis
df_analysis = prepare_data(df_data)

# Refactor date column
df_data.DATE = pd.DatetimeIndex(df_data.DATE).strftime("%Y-%m-%d")

# Load categories
df_categories = read_sql_table_cats(to_records=False, fill_nan_end_year=True).astype(
    {'begin_year': 'int', 'end_year': 'int'})

df_categories = df_categories[(df_categories.begin_year <= GenSet.year_selected) & (
        df_categories.end_year >= GenSet.year_selected)].drop(
    columns=['begin_year', 'end_year']).rename(columns={'grouplevel': 'group'})

df_categories.columns = df_categories.columns.str.upper()

df_budget = prepare_data_budget(pd.offsets.MonthEnd().rollforward(df_analysis['DATE'].max()), GenSet.year_selected)

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
def get_tables_for_selected_group(selected_value):
    global df_analysis, df_budget, month_names

    df_pivot_actuals = group_data_for_table(df_analysis, selected_value, 'AMOUNT_NW', month_names)
    df_pivot_budget = group_data_for_table(df_budget, selected_value, 'BUDGET', month_names)

    return df_pivot_actuals, df_pivot_budget


# Settings: import budget files
@app.callback(Output('checklist-remove-files', 'options', allow_duplicate=True),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              prevent_initial_call=True)
def import_file_and_update_database(list_of_contents, list_of_names):
    if list_of_contents is not None:
        for contents, filename in zip(list_of_contents, list_of_names):
            parse_contents_file_import(contents, filename)

        lst_source_files = files_in_budget()

        return get_label_style(lst_source_files)


# Settings: no file selected to remove
@app.callback(Output('modal-remove-file', 'is_open', allow_duplicate=True),
              Input('no-remove-file', 'n_clicks'),
              prevent_initial_call=True)
def close_no_selection(n_clicks):
    if n_clicks:
        return False


# Settings: delete file(s) from budget and update database
@app.callback(Output('modal-remove-file', 'is_open', allow_duplicate=True),
              Output('checklist-remove-files', 'options', allow_duplicate=True),
              Output('checklist-remove-files', 'value'),
              Input('yes-remove-file', 'n_clicks'),
              State('checklist-remove-files', 'value'),
              prevent_initial_call=True)
def del_files_from_budget(n_clicks, selection):
    if ctx.triggered[0]['prop_id'].split('.')[0] == 'yes-remove-file':
        src_files = delete_files_from_budget(selection)

        return False, get_label_style(src_files), []


# Settings: open modal to confirm if files need to be removed
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


# Settings: modal to remove category from table
@app.callback(Output('modal-remove', 'is_open', allow_duplicate=True),
              Output('table-category', 'data', allow_duplicate=True),
              Input('yes-remove', 'n_clicks'),
              Input('no-remove', 'n_clicks'),
              State('table-category', 'active_cell'),
              State('table-category', 'data'),
              prevent_initial_call=True
              )
def remove_or_keep_category(ny, nn, active_cell, data):
    row = data[active_cell['row']]

    if nn:
        df_cats = read_sql_table_cats(add_remove_emoji=True, add_edit_emoji=True)
        return False, df_cats
    if ny:
        remove_category(row)

        df_cats = read_sql_table_cats(add_remove_emoji=True, add_edit_emoji=True)

        return False, df_cats


# Settings: open modal to change category
@app.callback(Output('modal-edit', 'is_open'),
              Output('modal-remove', 'is_open'),
              Output('group-edit', 'value'),
              Output('category-edit', 'value'),
              Output('startyear-edit', 'value'),
              Output('endyear-edit', 'value'),
              Input('table-category', 'active_cell'),
              State('table-category', 'data')
              )
def open_modal_edit_category(active_cell, data):

    if not active_cell:
        return False, False, None, None, None, None

    row = data[active_cell['row']]

    if active_cell['column'] == 4:
        return True, False, row['grouplevel'], row['category'], row['begin_year'], row['end_year']
    elif active_cell['column'] == 5:
        return False, True, None, None, None, None
    else:
        return False, False, None, None, None, None


# Settings: submit changes from edit modal
@app.callback(Output('modal-edit', 'is_open', allow_duplicate=True),
              Output('table-category', 'data', allow_duplicate=True),
              # Input('close-edit', 'n_clicks'),
              Input('submit-cat-edit', 'n_clicks'),
              State('group-edit', 'value'),
              State('category-edit', 'value'),
              State('startyear-edit', 'value'),
              State('endyear-edit', 'value'),
              State('table-category', 'active_cell'),
              State('table-category', 'data'),
              prevent_initial_call=True)
def submit_changes_edit(n2, group, cat, sy, ey, active_cell, data):
    if ctx.triggered_id == 'close-edit':
        df_cats = read_sql_table_cats(add_edit_emoji=True, add_remove_emoji=True)
        return False, df_cats
    else:
        row = data[active_cell['row']]

        # remove current category
        remove_category(row)

        # insert changed category
        add_category((f'{group}_{cat}_{sy}', group, cat, sy, ey))

        df_cats = read_sql_table_cats(add_edit_emoji=True, add_remove_emoji=True)

        return False, df_cats


# Settings: add new category to database
@app.callback(
     Output("modal", "is_open"),
     Output('table-category', 'data'),
     Input("open", "n_clicks"),
     # Input("close", "n_clicks"),
     Input('submit-cat', 'n_clicks'),
     State("modal", "is_open"),
     State('group', 'value'),
     State('category', 'value'),
     State('startyear', 'value'),
     State('endyear', 'value'),
)
def add_new_category(n1, n3, is_open, group, cat, startyear, endyear):

    df_cats = read_sql_table_cats(add_remove_emoji=True, add_edit_emoji=True)

    if not ctx.triggered_id:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered_id

    if button_id == 'submit-cat':
        # todo: check input

        params = (f'{group}_{cat}_{startyear}', group, cat, startyear, endyear)
        add_category(params)

        df_cats = read_sql_table_cats(add_remove_emoji=True, add_edit_emoji=True)

        return not is_open, df_cats

    if button_id == 'open' or button_id == 'close':
        return not is_open, df_cats

    return is_open, df_cats


# Budget vs Actuals: table with sum per category for actuals and budget
@app.callback(Output('data-view', 'data'),
              [Input('dropdown-view', 'value')])
def create_table_output(view_value):

    df_raw = read_sql_table_transactions(year=GenSet.year_selected, test_par=GenSet.test_par).sort_values(
        by='DATE', ascending=False)

    df_raw = df_raw[df_raw.GROUP != 'Inkomsten'].copy()

    df_act = prepare_data(df_raw)

    if view_value == 'YTD':
        ref_date = pd.offsets.MonthEnd().rollforward(df_raw.DATE.max())

        df_bud = prepare_data_budget(ref_date=ref_date,
                                     sel_year=GenSet.year_selected,
                                     exclude_income=True,
                                     rename_budget=False)

        df_act = df_act[df_act['DATE'] < ref_date.strftime('%Y-%m-%d')]
    else:
        df_bud = prepare_data_budget(ref_date=None,
                                     sel_year=GenSet.year_selected,
                                     exclude_income=True,
                                     rename_budget=False)

    df_act_tot = df_act.groupby('CATEGORY')['AMOUNT_NW'].sum()
    df_bud_tot = df_bud.groupby('CATEGORY')['BUDGET'].sum()

    df_tot = pd.concat([df_bud_tot, df_act_tot], axis=1).fillna(0).sort_values(
        by='AMOUNT_NW', ascending=False)

    df_tot.loc['Total'] = df_tot.sum()

    df_tot['DELTA'] = df_tot['BUDGET'] - df_tot['AMOUNT_NW']
    df_tot['RATIO'] = df_tot['AMOUNT_NW'] / df_tot['BUDGET']

    return df_tot.reset_index().round(2).to_dict('records')


# Data: add row to table
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


# Data: show duplicate transactions
@app.callback(
    Output('modal-duplicate-trans', 'is_open', allow_duplicate=True),
    Output('data-duplicates', 'data'),
    Input('duplicate-trans-button', 'n_clicks'),
    State("page-2-content", "data"),
    prevent_initial_call=True
)
def show_duplicates(n_clicks, table):
    if n_clicks > 0:

        df_dup = pd.DataFrame(table)[['TRANS_ID', 'DATE', 'PARTY', 'AMOUNT']]

        return True, df_dup[df_dup.duplicated()].to_dict('records')
    else:
        return False, None


@app.callback(
    Output('modal-transactions-saved', 'is_open'),
    Input("save-button", "n_clicks"),
    State("page-2-content", "data"))
def export_data_to_excel(nclicks, table1):
    if nclicks > 0:
        global df_categories

        df_out = pd.DataFrame(table1)
        df_out['DATE'] = pd.to_datetime(df_out['DATE'], format='%Y-%m-%d')
        df_out['TRANS_ID'] = df_out['TRANS_ID'].apply(lambda x: uuid.uuid4() if ((x == '') or (x is None)) else x)
        df_out['TRANSACTION_TYPE'] = df_out['TRANSACTION_TYPE'].apply(lambda x: '-' if x == '' else x)

        df_out = df_out.drop('GROUP', axis=1).merge(
            df_categories, how='left', left_on='CATEGORY', right_on='CATEGORY')

        add_transactions_to_db(df_out, test_par=GenSet.test_par)

        return True


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
    filenames_rabobank = next(os.walk(GenSet.project_path / f'data/Rabobank'), (None, None, []))[2]
    filenames_asn_bank = next(os.walk(GenSet.project_path / f'data/ASN Bank'), (None, None, []))[2]

    if filenames_rabobank:
        df_rabo = ReadRabo().run(filenames_rabobank)
        df_rabo = FindCategory().run(df_rabo, 'Rabobank')
        add_transactions_to_db(df_rabo, test_par=GenSet.test_par)

    if filenames_asn_bank:
        df_asn = ReadAsn().run(filenames_asn_bank)
        df_asn = FindCategory().run(df_asn, 'ASN Bank')
        add_transactions_to_db(df_asn, test_par=GenSet.test_par)

    app.run_server(debug=GenSet.debug)


if __name__ == '__main__':
    run()
