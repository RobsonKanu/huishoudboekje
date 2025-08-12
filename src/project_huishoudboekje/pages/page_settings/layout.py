
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import html, dcc, dash_table

from project_huishoudboekje.pages.page_settings import page_components
from project_huishoudboekje.database import read_sql_table_cats, files_in_budget


def create_layout(navbar):
    df_cats = read_sql_table_cats(add_remove_emoji=True, add_edit_emoji=True)

    checklist_source_files = dcc.Checklist(
        files_in_budget(),
        id='checklist-remove-files'
    )

    return html.Div([
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
                page_components.modal_remove_file,
                page_components.modal_no_selection,
            ], style={'width': '33%', 'padding': '10px', 'float': 'left'}),
        ]),
        html.Div([
            page_components.modal_edit,
            page_components.modal_remove,
            html.Div([

                html.H3("Categories", style={'text-align': 'left'}),

                dash_table.DataTable(
                    id='table-category',
                    columns=[{'name': 'GROUP', 'id': 'grouplevel'},
                             {'name': 'CATEGORY', 'id': 'category'},
                             {'name': 'START', 'id': 'begin_year'},
                             {'name': 'END', 'id': 'end_year'},
                             {'name': 'EDIT', 'id': 'edit'},
                             {'name': 'REMOVE', 'id': 'remove'}],
                    data=df_cats,
                    style_table={'height': '500px', 'overflowY': 'scroll'},
                    style_as_list_view=True,
                    style_cell={'padding': '5px', 'font_family': 'sans-serif', 'font_size': '12px',
                                'textAlign': 'left'},
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'},
                        {'if': {'column_id': 'begin_year'}, 'textAlign': 'right'},
                        {'if': {'column_id': 'end_year'}, 'textAlign': 'right'},
                        {'if': {'column_id': 'remove'}, 'textAlign': 'center'},
                        {'if': {'column_id': 'edit'}, 'textAlign': 'center'}
                    ],
                    style_header={'backgroundColor': px.colors.qualitative.Dark2[2], 'fontWeight': 'bold',
                                  'color': 'white'}
                ),
                page_components.modal_add_category,
            ], style={'width': '95%', 'padding': '10px', 'float': 'left'})
        ], style={'display': 'flex', 'height': '100%', 'margin-left': '4px', 'margin-right': '4px', 'margin-top': '4px'})
    ])
