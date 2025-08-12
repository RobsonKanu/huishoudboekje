
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import html, dash_table

from project_huishoudboekje.pages.page_data.page_components import button_style, create_dash_table_data


def create_layout(navbar, df_data, df_categories):
    return html.Div([
        navbar,
        create_dash_table_data(df_data, df_categories),
        html.Button('Add transaction', id='editing-rows-button', n_clicks=0,
                    style=button_style),
        html.Button('Check duplicate transations', id='duplicate-trans-button', n_clicks=0,
                    style=button_style),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Duplicate transactions")),
                dbc.ModalBody(
                    dash_table.DataTable(id='data-duplicates',
                                         style_table={'overflowX': 'scroll'},
                                         style_header={'backgroundColor': px.colors.qualitative.Pastel2[2],
                                                       'fontWeight': 'bold'},
                                         style_as_list_view=True,
                                         style_cell={'padding': '1px', 'font_family': 'sans-serif',
                                                     'font_size': '12px'},
                                         style_data_conditional=[
                                             {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
                                         page_current=0,
                                         # page_size=15,
                                         )
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button("Close", id="close-modal-duplicate-trans", className="ms-auto", n_clicks=0)
                    ])
                ),
            ],
            id="modal-duplicate-trans",
            is_open=False,
            size='xl'
        ),
        html.Button(id="save-button", n_clicks=0, children="Save",
                    style=button_style),
        html.Div(id="output-1", children="Press button to save changes"),
    ])
