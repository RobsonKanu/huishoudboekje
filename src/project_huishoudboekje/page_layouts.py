
import plotly.express as px
from dash import dash_table, Dash, html, dcc
from dash.dash_table.Format import Format
import dash_bootstrap_components as dbc

from project_huishoudboekje.config import TableSettings


def get_nav_bar():

    return dbc.Navbar(
                dbc.Container(
                    [
                        html.A(
                            dbc.Row([
                                dbc.Col(dbc.NavbarBrand("Huidhoudboekje Rob & Anne Schuitemaker", className="ms-2"))
                            ], align="center", className="g-0"), href="/", style={"textDecoration": "none"}
                        ),
                        dbc.Row([
                            dbc.NavbarToggler(id="navbar-toggler"),
                            dbc.Collapse([
                                dbc.Nav([
                                    dbc.NavItem(dbc.NavLink("Dashboard", href="/dashboard")),
                                    dbc.NavItem(dbc.NavLink("Budget vs Actuals", href="/budget")),
                                    dbc.NavItem(dbc.NavLink("Data", href="/data")),
                                    dbc.NavItem(dbc.NavLink('Settings', href="/settings")),
                                ], className="w-100")
                            ], id="navbar-collapse", is_open=False, navbar=True)
                        ], className="flex-grow-1"),
                    ],
                    fluid=True,
                ),
                dark=True,
                color=px.colors.qualitative.Dark2[2],
                style={'margin-bottom': '2px'}
            )


def get_page_1_graphs(fig_totals, fig_groups, fig_group_month):

    return html.Div([
        html.Div([dcc.Graph(id='total-graph', figure=fig_totals, style={'width': '95vh', 'height': '25vh'}),
                  dcc.Graph(id='group-graph', figure=fig_groups, style={'width': '95vh', 'height': '25vh'})
                  ], style={'width': '49%'}),
        html.Div([dcc.Graph(id='group-month-graph', figure=fig_group_month, style={'width': '95vh', 'height': '50vh'})
                  ], style={'width': '49%'})
    ], style={'height': '70%', 'display': 'flex', 'margin-bottom': '4px'})


def get_page_1_selector(available_groups):

    return html.Div([
        html.I("Select category: ", style={'width': '130px', 'height': '35px', 'padding-top': '7px',
                                           'textAlign': 'center', 'font-family': 'sans-serif',
                                           'font-style': 'normal'}),
        dcc.Dropdown(id='dropdown-groups',
                     options=[{'label': i, 'value': i} for i in available_groups],
                     value='Inkomsten',
                     style={'width': '300px', 'height': '35px', 'font-family': 'sans-serif',
                            'font-style': 'normal', 'font-size': '14px'})
    ], style={'display': 'flex'})


def get_page_1_table_actuals(month_names):

    return html.Div([
        dash_table.DataTable(
            id='data-groups',
            columns=[{'id': 'CATEGORY', 'name': 'Actuals'}] + [
                {'id': i, 'name': i, 'type': 'numeric', 'format': TableSettings().euro_format} for i in month_names] + \
                    [{'id': 'Total', 'name': 'Total', 'type': 'numeric', 'format': TableSettings().euro_format}],
            style_table={'height': '250px', 'overflowY': 'scroll'},
            style_cell_conditional=[{'if': {'column_id': 'CATEGORY'}, 'textAlign': 'left'}],
            style_as_list_view=True,
            style_cell={'padding': '5px', 'font_family': 'sans-serif', 'font_size': '12px'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'},
                {"if": {"column_id": "Total"}, "fontWeight": "bold",
                 'backgroundColor': px.colors.qualitative.Pastel2[2]},
                {'if': {'filter_query': '{{CATEGORY}} = {}'.format("Total"),},
                 'backgroundColor': px.colors.qualitative.Set2[2], 'color': 'white'}
            ],
            style_header={'backgroundColor': px.colors.qualitative.Dark2[2], 'fontWeight': 'bold', 'color': 'white'}
        ),
        ], style={'height': '25%', 'margin-left': '4px', 'margin-right': '4px', 'margin-top': '4px'})


def get_page_1_table_budget(month_names):

    return html.Div([
        dash_table.DataTable(
            id='data-groups-budget',
            columns=[{'id': 'CATEGORY', 'name': 'Budget'}] + [
                {'id': i, 'name': i, 'type': 'numeric', 'format': TableSettings().euro_format} for i in month_names] + \
                    [{'id': 'Total', 'name': 'Total', 'type': 'numeric', 'format': TableSettings().euro_format}],
            style_table={'height': '250px', 'overflowY': 'scroll'},
            style_cell_conditional=[{'if': {'column_id': 'CATEGORY'}, 'textAlign': 'left'}],
            style_as_list_view=True,
            style_cell={'padding': '5px', 'font_family': 'sans-serif', 'font_size': '12px'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'},
                {"if": {"column_id": "Total"}, "fontWeight": "bold",
                 'backgroundColor': px.colors.qualitative.Pastel2[2]},
                {'if': {'filter_query': '{{CATEGORY}} = {}'.format("Total"),},
                 'backgroundColor': px.colors.qualitative.Set2[2], 'color': 'white'}
            ],
            style_header={'backgroundColor': px.colors.qualitative.Dark2[2], 'fontWeight': 'bold', 'color': 'white'},
        ),
    ], style={'height': '25%', 'margin-left': '4px', 'margin-right': '4px', 'margin-top': '4px'})


def get_page_2_table(df, df_categories):

    return html.Div([
        dash_table.DataTable(
            id='page-2-content',
            columns=[
                {'name': 'TRANS_ID', 'id': 'TRANS_ID'},
                {'name': 'DATE', 'id': 'DATE', 'type': 'datetime'},
                {'name': 'SOURCE', 'id': 'SOURCE', 'presentation': 'dropdown'},
                {'name': 'TRANSACTION TYPE', 'id': 'TRANSACTION_TYPE', 'type': 'text'},
                {'name': 'FINANCIAL TYPE', 'id': 'FINANCIAL_TYPE', 'presentation': 'dropdown'},
                {'name': 'PARTY', 'id': 'PARTY', 'type': 'text'},
                {'name': 'AMOUNT', 'id': 'AMOUNT', 'type': 'numeric', 'format': TableSettings().euro_format},
                {'name': 'CATEGORY', 'id': 'CATEGORY', 'presentation': 'dropdown'},
                {'name': 'ANALYSE INDICATOR', 'id': 'ANALYSE_IND', 'type': 'numeric', 'format': Format(precision=0)},
                {'name': 'GROUP', 'id': 'GROUP'}
            ],
            hidden_columns=['TRANS_ID', 'TRANSACTION_TYPE', 'GROUP'],
            data=df.to_dict('records'),
            editable=True,
            row_deletable=True,
            filter_action="native",
            sort_action="native",
            style_table={'overflowX': 'scroll'},
            style_header={'backgroundColor': px.colors.qualitative.Pastel2[2], 'fontWeight': 'bold'},
            style_as_list_view=True,
            style_cell={'padding': '1px', 'font_family': 'sans-serif', 'font_size': '12px'},
            style_data_conditional=[{'if': {'row_index': 'odd'}, 'backgroundColor': 'rgb(220, 220, 220)'}],
            css=[{"selector": ".show-hide", "rule": "display: none"},
                 {"selector": ".Select-menu-outer", "rule": "display: block !important"}],
            page_current=0,
            page_size=15,
            dropdown={
                'FINANCIAL_TYPE': {
                    'options': [{'label': 'debet', 'value': 'debet'}, {'label': 'credit', 'value': 'credit'}]
                },
                'CATEGORY': {
                    'options': [{'label': cat, 'value': cat} for cat in df_categories['CATEGORY'].tolist()]
                },
                'SOURCE': {
                    'options': [{'label': 'Rabobank', 'value': 'Rabobank'},
                                {'label': 'ASN Bank', 'value': 'ASN Bank'},
                                {'label': 'Contant', 'value': 'Contant'}]
                }
            }
        ),
    ], style={'margin-left': '4px', 'margin-right': '4px'})


def get_page_2_button():

    return {
        'backgroundColor': px.colors.qualitative.Pastel2[2],
        'font-family': 'sans-serif',
        'font-size': '14px',
        'border': 'none',
        'margin-left': '2px',
        'margin-right': '2px'
    }

