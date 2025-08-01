
import plotly.express as px
import dash_bootstrap_components as dbc
from dash import dash_table, Dash, html, dcc, ctx
from dash.dependencies import Input, Output, State
from dash.dash_table import FormatTemplate

import uuid
import numpy as np
import pandas as pd
import base64
import io

from datetime import date

from project_huishoudboekje.config import GeneralSettings, TableSettings, AppSettings
from project_huishoudboekje.graphs import \
    graph_group_month, graph_groups, graph_total, graph_total_delta, graph_groups_delta
from project_huishoudboekje.page_layouts import get_nav_bar, get_page_1_graphs, get_page_1_selector, \
    get_page_1_table_actuals, get_page_1_table_budget, get_page_2_table, get_page_2_button
from project_huishoudboekje.database import (
    connect_to_database, read_sql_table_cats, files_in_budget, delete_files_from_budget,
    remove_category, add_budget_file_to_db, read_sql_table_budget)


class App(object):
    def run(self):

        # Year used in dashboard
        sel_year = GeneralSettings.year_selected

        # Load data transactions
        df = pd.read_excel(GeneralSettings.project_path / 'data/processed/transactions.xlsx').sort_values(
            by='DATE', ascending=False)

        # Filter data for selected year
        df = df[(df['DATE'] >= f'{sel_year}-01-01') & (df['DATE'] < f'{sel_year+1}-01-01')].copy(deep=True)

        # Load categories
        df_categories = read_sql_table_cats(to_records=False, fill_nan_end_year=True).astype(
            {'begin_year': 'int', 'end_year': 'int'})

        df_categories = df_categories[(df_categories.begin_year <= sel_year) & (df_categories.end_year >= sel_year)].drop(
            columns=['begin_year', 'end_year']).rename(columns={'grouplevel': 'group'})

        df_categories.columns = df_categories.columns.str.upper()

        # Prepare data for analysis
        df_analysis = self.prepare_data(df)
        df_budget = self.prepare_data_budget(df_analysis['DATE'].max(), sel_year)

        # Get all unique groups
        available_groups = df_analysis.GROUP.unique()

        # List of months for table use
        month_names = [f'{sel_year}-0' + str(i) for i in list(range(1, 10))] + [
            f'{sel_year}-' + str(i) for i in list(range(10, 13))]

        # Get graphs
        fig_group_month = graph_group_month(df_analysis)
        fig_groups = graph_groups(df_analysis, 'Totals by expense group')
        fig_totals = graph_total(df_analysis, "Total income and expenses per month")

        fig_totals_actual = graph_total(df_analysis, 'Actual')
        fig_groups_actual = graph_groups(df_analysis, 'Actual')
        fig_groups_budget = graph_groups(df_budget, 'Budget')
        fig_totals_budget = graph_total(df_budget, 'Budget')

        fig_totals_delta = graph_total_delta(df_budget, df_analysis)
        fig_groups_delta = graph_groups_delta(df_budget, df_analysis)

        # Refactor date column
        df.DATE = pd.DatetimeIndex(df.DATE).strftime("%Y-%m-%d")

        # Initialize app
        app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=AppSettings().style_sheet)

        app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ])

        navbar = get_nav_bar()

        page_1_layout = html.Div([
            navbar,
            get_page_1_graphs(fig_totals, fig_groups, fig_group_month),
            get_page_1_selector(available_groups),
            get_page_1_table_actuals(month_names),
            get_page_1_table_budget(month_names)
        ])

        @app.callback(Output('data-groups', 'data'),
                      [Input('dropdown-groups', 'value')])
        def update_rows(selected_value):
            df_sel = pd.pivot_table(df_analysis[df_analysis.GROUP == selected_value], values='AMOUNT_NW',
                                    index=['CATEGORY'], columns=['YEAR_MONTH'], aggfunc=np.sum).reset_index()

            for col in month_names:
                if col not in df_sel.columns:
                    df_sel[col] = 0.0

            df_sel['Total'] = df_sel[month_names].sum(axis=1)
            df_sel = df_sel.fillna(0).sort_values(by=['CATEGORY'], ascending=True)
            df_sel.loc['Total'] = df_sel.sum()
            df_sel.loc['Total', 'CATEGORY'] = 'Total'

            return df_sel.round(2).to_dict('records')

        @app.callback(Output('data-groups-budget', 'data'),
                      [Input('dropdown-groups', 'value')])
        def update_rows_budget(selected_value):
            df_budget = read_sql_table_budget(year=GeneralSettings.year_selected)
            # df_budget = pd.read_excel(GeneralSettings.project_path / f'data/budget{GeneralSettings.year_selected}.xlsx')

            df_sel = pd.pivot_table(df_budget[df_budget.GROUP == selected_value], values='BUDGET',
                                    index=['CATEGORY'], columns=['YEAR_MONTH'], aggfunc=np.sum).reset_index()

            for col in month_names:
                if col not in df_sel.columns:
                    df_sel[col] = 0.0

            df_sel['Total'] = df_sel[month_names].sum(axis=1)
            df_sel = df_sel.fillna(0).sort_values(by=['CATEGORY'], ascending=True)
            df_sel.loc['Total'] = df_sel.sum()
            df_sel.loc['Total', 'CATEGORY'] = 'Total'

            return df_sel.round(2).to_dict('records')

        page_2_layout = html.Div([
            navbar,
            get_page_2_table(df, df_categories),
            html.Button('Add transaction', id='editing-rows-button', n_clicks=0,
                        style=get_page_2_button()),
            html.Button(id="save-button", n_clicks=0, children="Save",
                        style=get_page_2_button()),
            html.Div(id="output-1", children="Press button to save changes"),
        ])

        width_figures = '450px'

        page_3_layout = html.Div([
            navbar,
            html.Br(),
            html.Div([
                html.Div(
                    [html.I("Total income and expenses per month", style={'font-family': 'sans-serif',
                                                   'font-style': 'normal'})],
                    style={'width': '29%', 'backgroundColor': px.colors.qualitative.Pastel2[2], 'padding': '5px',
                           'margin-left': '20px', 'margin-right': '20px', 'textAlign': 'center'}),
                html.Div(
                    [html.I("Totals by expense group", style={'width': '130px', 'height': '35px', 'padding-top': '7px',
                                                   'padding-left': '7px',
                                                   'textAlign': 'center', 'font-family': 'sans-serif',
                                                   'font-style': 'normal'})],
                    style={'width': '29%', 'backgroundColor': px.colors.qualitative.Pastel2[2], 'padding': '5px',
                           'margin-left': '20px', 'margin-right': '20px', 'textAlign': 'center'}),
                html.Div(
                    [html.I("Comparison per category", style={'width': '130px', 'height': '35px', 'padding-top': '7px',
                                                       'padding-left': '7px',
                                                       'textAlign': 'center', 'font-family': 'sans-serif',
                                                       'font-style': 'normal'})],
                    style={'width': '40%', 'backgroundColor': px.colors.qualitative.Pastel2[2], 'padding': '5px',
                           'margin-left': '20px', 'margin-right': '20px', 'textAlign': 'center'})],
                style={'display': 'flex'}
            ),
            html.Br(),
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='total-graph', figure=fig_totals_actual, style={'width': width_figures, 'height': '25vh'}),
                    dcc.Graph(
                        id='total-graph', figure=fig_totals_budget, style={'width': width_figures, 'height': '25vh'}),
                    dcc.Graph(
                        id='total-graph', figure=fig_totals_delta, style={'width': width_figures, 'height': '25vh'})
                ], style={'width': '29%', 'margin-left': '10px', 'margin-right': '0px'}),
                html.Div([
                    dcc.Graph(
                        id='group-graph', figure=fig_groups_actual, style={'width': width_figures, 'height': '25vh'}),
                    dcc.Graph(
                        id='group-graph', figure=fig_groups_budget, style={'width': width_figures, 'height': '25vh'}),
                    dcc.Graph(
                        id='group-graph', figure=fig_groups_delta, style={'width': width_figures, 'height': '25vh'})
                ], style={'width': '29%', 'margin-left': '10px', 'margin-right': '0px'}),
                html.Div([
                    html.Div([
                        html.I("Select view: ", style={'width': '130px', 'height': '35px', 'padding-top': '7px',
                                                       'padding-left': '7px',
                                                       'textAlign': 'left', 'font-family': 'sans-serif',
                                                       'font-style': 'normal'}),
                        dcc.Dropdown(id='dropdown-view',
                                     options=[{'label': i, 'value': i} for i in ['Total', 'YTD']],
                                     value='YTD',
                                     style={'width': '100px', 'height': '35px', 'font-family': 'sans-serif',
                                            'font-style': 'normal', 'font-size': '14px'})
                    ], style={'display': 'flex'}),
                    html.Div([
                        dash_table.DataTable(
                            id='data-view', columns=[
                                {'id': 'CATEGORY', 'name': 'Category'},
                                {'id': 'BUDGET', 'name': 'Budget', 'type': 'numeric',
                                 'format': TableSettings().euro_format},
                                {'id': 'AMOUNT_NW', 'name': 'Actuals', 'type': 'numeric',
                                 'format': TableSettings().euro_format},
                                {'id': 'DELTA', 'name': 'Delta', 'type': 'numeric',
                                 'format': TableSettings().euro_format},
                                {'id': 'RATIO', 'name': 'Ratio', 'type': 'numeric',
                                 'format': FormatTemplate.percentage(0)}],
                            style_table={'height': '500px', 'overflowY': 'scroll'},
                            style_cell_conditional=[{'if': {'column_id': 'CATEGORY'}, 'textAlign': 'left'}],
                            style_as_list_view=True,
                            style_cell={'padding': '5px', 'font_family': 'sans-serif', 'font_size': '12px'},
                            style_data_conditional=[
                                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'},
                                {"if": {"column_id": "Total"}, "fontWeight": "bold",
                                 'backgroundColor': px.colors.qualitative.Pastel2[2]},
                                {'if': {'filter_query': '{{CATEGORY}} = {}'.format("Total"),},
                                 'backgroundColor': px.colors.qualitative.Set2[2], 'color': 'white'},
                                {'if': {'filter_query': '{RATIO} > 1', 'column_id': 'RATIO'},
                                 'backgroundColor': '#EF553B', 'color': 'white'},
                                {'if': {'filter_query': '{RATIO} < 1', 'column_id': 'RATIO'},
                                 'backgroundColor': '#B6E880'}],
                            style_header={
                                'backgroundColor': px.colors.qualitative.Dark2[2],
                                'fontWeight': 'bold', 'color': 'white'}
                        )
                    ], style={'height': '100%', 'margin-left': '4px', 'margin-right': '4px', 'margin-top': '4px'})
                ], style={'width': '40%', 'margin-left': '20px', 'margin-right': '20px'})
            ], style={'height': '100%', 'display': 'flex', 'margin-bottom': '4px'})
        ])

        modal = html.Div(
            [
                dbc.Button("Add category", id="open", n_clicks=0,
                           style={'background-color': px.colors.qualitative.Dark2[2],
                                  'border-width': '0px',
                                  'textAlign': 'left'}),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Header")),
                        dbc.ModalBody(
                            html.Div([
                                html.Div(['Group', dbc.Input(id='group')]),
                                html.Div(['Category', dbc.Input(id='category')]),
                                html.Div(['Start', dbc.Input(id='startyear')]),
                                html.Div(['End', dbc.Input(id='endyear')])
                            ])
                        ),
                        dbc.ModalFooter(
                            html.Div([
                                dbc.Button("Submit", id="submit-cat", n_clicks=0),
                                dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)
                            ])
                        ),
                    ],
                    id="modal",
                    is_open=False,
                ),
            ]
        )

        modal_edit = html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Header")),
                        dbc.ModalBody(
                            html.Div([
                                html.Div(['Group', dbc.Input(id='group-edit')]),
                                html.Div(['Category', dbc.Input(id='category-edit')]),
                                html.Div(['Start', dbc.Input(id='startyear-edit')]),
                                html.Div(['End', dbc.Input(id='endyear-edit')])
                            ])
                        ),
                        dbc.ModalFooter(
                            html.Div([
                                dbc.Button("Submit", id="submit-cat-edit", n_clicks=0),
                                dbc.Button("Close", id="close-edit", className="ms-auto", n_clicks=0)
                            ])
                        ),
                    ],
                    id="modal-edit",
                    is_open=False,
                ),
            ]
        )

        modal_remove = html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalBody(
                            'Wil je deze categorie verwijderen?'
                        ),
                        dbc.ModalFooter(
                            html.Div([
                                dbc.Button("Yes", id="yes-remove", n_clicks=0),
                                dbc.Button("No", id="no-remove", className="ms-auto", n_clicks=0)
                            ])
                        ),
                    ],
                    id="modal-remove",
                    is_open=False,
                ),
            ]
        )

        df_cats = read_sql_table_cats()

        cursor, conn = connect_to_database()

        df_budget_sources = pd.read_sql("""SELECT * FROM budget""", conn)

        cursor.close()
        conn.close()

        checklist_source_files = dcc.Checklist(
            df_budget_sources.source_file.unique(),
            id='checklist-remove-files'
        )

        modal_remove_file = html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalBody(
                            'Wil je de geselecteerde bestanden verwijderen?'
                        ),
                        dbc.ModalFooter(
                            html.Div([
                                dbc.Button("Yes", id="yes-remove-file", n_clicks=0),
                                dbc.Button("No", id="no-remove-file", className="ms-auto", n_clicks=0)
                            ])
                        ),
                    ],
                    id="modal-remove-file",
                    is_open=False,
                ),
            ]
        )

        modal_no_selection = html.Div(
            [
                dbc.Modal(
                    [
                        dbc.ModalBody(
                            'Geen bestand geselecteerd.'
                        ),
                        dbc.ModalFooter(
                            html.Div([
                                dbc.Button("Close", id="no-selection-close", n_clicks=0),
                            ])
                        ),
                    ],
                    id="modal-no-selection",
                    is_open=False,
                ),
            ]
        )

        page_settings_layout = html.Div([
            navbar,
            html.Div([
                html.Div([
                    html.Div(
                        [html.I("Input files Budget",
                                style={'width': '130px', 'height': '35px', 'padding-top': '7px',
                                       'padding-left': '7px',
                                       'textAlign': 'center', 'font-family': 'sans-serif',
                                       'font-style': 'normal'})],
                        style={'width': '29%', 'backgroundColor': px.colors.qualitative.Pastel2[2], 'padding': '5px',
                               'margin-left': '20px', 'margin-right': '20px', 'textAlign': 'center'}),
                    html.Div([
                        dbc.Button("Remove files", id="remove-files", n_clicks=0),
                        dcc.Upload(
                            id='upload-data',
                            children=html.Div([
                                'Drag and Drop or ',
                                html.A('Add Files')
                            ]),
                            multiple=True),
                        ], style={'display': 'flex', 'justifyContent': 'space-around'}),
                    checklist_source_files,
                    modal_remove_file,
                    modal_no_selection,
                ], style={'width': '33%', 'padding': '10px', 'float': 'left'}),
            ]),
            html.Div([
                modal,
                modal_edit,
                modal_remove,
                html.Div([

                    html.H3("Categories", style={'text-align': 'center'}),

                    dash_table.DataTable(
                        id='table-category',
                        columns=[{'name': 'GROUP', 'id': 'grouplevel'},
                                 {'name': 'CATEGORY', 'id': 'category'},
                                 {'name': 'START', 'id': 'begin_year'},
                                 {'name': 'END', 'id': 'end_year'},
                                 {'name': 'EDIT', 'id': 'edit'},
                                 {'name': 'REMOVE', 'id': 'remove'}],
                        data=df_cats
                    )
                ], style={'width': '66%', 'padding': '10px', 'float': 'left'})
            ], style={'display': 'flex'})
        ])

        def parse_contents(contents, filename):
            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)
            try:
                if 'csv' in filename:
                    # Assume that the user uploaded a CSV file
                    df = pd.read_csv(
                        io.StringIO(decoded.decode('utf-8')))
                elif 'xlsx' in filename:
                    # Assume that the user uploaded an excel file
                    df = pd.read_excel(io.BytesIO(decoded))
            except Exception as e:
                print(e)
                return html.Div([
                    'There was an error processing this file.'
                ])

            # todo: open modal if file already exists 'message first remove file before importing again'
            add_budget_file_to_db(df, filename)

        @app.callback(Output('checklist-remove-files', 'options', allow_duplicate=True),
                      Input('upload-data', 'contents'),
                      State('upload-data', 'filename'),
                      prevent_initial_call=True)
        def update_output(list_of_contents, list_of_names):
            if list_of_contents is not None:
                for c, n in zip(list_of_contents, list_of_names):
                    parse_contents(c, n)

                lst_source_files = files_in_budget()

                return lst_source_files

        @app.callback(Output('modal-no-selection', 'is_open', allow_duplicate=True),
                      Input('no-selection-close', 'n_clicks'),
                      prevent_initial_call=True)
        def close_no_selection(n_clicks):
            if n_clicks:
                return False

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

                cursor.close()
                conn.close()

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

            df_analysis = self.prepare_data(df)

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
            Output("output-1", "children"),
            [Input("save-button", "n_clicks")],
            [State("page-2-content", "data")]
        )
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
        @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
        def display_page(pathname):
            if pathname == '/dashboard':
                return page_1_layout
            elif pathname == '/data':
                return page_2_layout
            elif pathname == '/budget':
                return page_3_layout
            elif pathname == '/settings':
                return page_settings_layout
            else:
                return page_1_layout
            # You could also return a 404 "URL not found" page here

        app.run_server(debug=False)


    def prepare_data(self, df):

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


    def prepare_data_budget(self, ref_date, sel_year):

        # df = pd.read_excel(GeneralSettings.project_path / f'data/budget{sel_year}.xlsx')
        df = read_sql_table_budget(year=GeneralSettings.year_selected)
        df['DATE'] = pd.to_datetime(df['YEAR_MONTH'], format='%Y-%m')

        df['AMOUNT_NW'] = df.apply(lambda x: x['BUDGET'] if x['GROUP'] == 'Inkomsten' else x['BUDGET'], axis=1)

        df['INCOME_IND'] = df['GROUP'].apply(lambda x: x if x == 'Inkomsten' else 'Uitgaven')

        return df[(df.DATE >= pd.to_datetime(f'{sel_year}-01-01')) & (df.DATE <= ref_date)].copy(deep=True)

