
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import html, dcc, dash_table

from project_huishoudboekje.pages.page_settings import page_components
from project_huishoudboekje.database import read_sql_table_budget, read_sql_table_cats


def create_layout(navbar):
    df_cats = read_sql_table_cats()
    df_budget_sources = read_sql_table_budget()

    checklist_source_files = dcc.Checklist(
        df_budget_sources.source_file.unique(),
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
            page_components.modal_add_category,
            page_components.modal_edit,
            page_components.modal_remove,
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
