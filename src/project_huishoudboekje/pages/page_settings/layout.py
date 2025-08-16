
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import html, dcc, dash_table

from project_huishoudboekje.pages.page_settings import page_components
from project_huishoudboekje.database import read_sql_table_cats, files_in_budget
from project_huishoudboekje.utils.general_components import get_label_style


def create_layout(navbar):
    df_cats = read_sql_table_cats(add_remove_emoji=True, add_edit_emoji=True)

    checklist_source_files = dcc.Checklist(
        options=get_label_style(files_in_budget()),
        id='checklist-remove-files',
        labelStyle={"width": "350px"},
        style={'display': 'inline-block',
               'padding-left': '10px',
               'border-radius': '5px',
               'backgroundColor': px.colors.qualitative.Pastel2[2]}
    )

    return html.Div([
        navbar,
        html.Div([
            html.Div([
                html.Div(
                    [
                        html.H3("Budget", style={'textAlign': 'left'})
                    ],
                ),
                html.Div([
                    html.H5('Files in budget'),
                    checklist_source_files,
                ], style={'width': '400px', 'margin-top': '10px', 'margin-bottom': '10px'}),
                html.Div([
                    dcc.Upload(
                        id='upload-data',
                        children=html.Div([html.A('Add Files')]),
                        multiple=True,
                        style={'background-color': px.colors.qualitative.Dark2[2],
                               'border-width': '0px',
                               'color': '#fff',
                               'padding': '5px',
                               'border-radius': '6px',
                               # 'margin-right': '10px',
                               'textAlign': 'center',
                               'width': '200px'}
                    ),
                ], style={'width': '100%', 'display': 'flex', 'margin-bottom': '10px'}),
                html.Div([
                    dbc.Button("Remove files", id="remove-files", n_clicks=0,
                               style={'background-color': px.colors.qualitative.Dark2[2],
                                      'border-width': '0px',
                                      'width': '200px'}
                               ),
                ], style={'width': '100%', 'display': 'flex'}),
                page_components.modal_remove_file,
                page_components.modal_no_selection,
            ], style={'width': '30%', 'padding': '0px', 'float': 'left'}),
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
                    fixed_rows={'headers': True},
                    style_table={'height': '500px'},
                    style_as_list_view=True,
                    style_cell={'padding': '5px', 'font_family': 'sans-serif', 'font_size': '12px',
                                'textAlign': 'center'},
                    style_data_conditional=[
                        {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'},
                        {'if': {'state': 'selected', 'row_index': 'odd'},
                         'backgroundColor': 'rgb(220, 220, 220)',
                         "border": "0px",
                         },
                        {'if': {'state': 'selected', 'row_index': 'even'},
                         'backgroundColor': 'white',
                         "border": "0px",
                         }
                    ],
                    style_header={'backgroundColor': px.colors.qualitative.Dark2[2], 'fontWeight': 'bold',
                                  'color': 'white', 'textAlign': 'center'}
                ),
                page_components.modal_add_category,
            ], style={'width': '100%', 'padding': '0px', 'float': 'left', 'margin-right': '10px'})
        ], style={'width': '60%', 'display': 'flex', 'height': '100%', 'margin-left': '4px', 'margin-right': '4px', 'margin-top': '4px'})
    ])
