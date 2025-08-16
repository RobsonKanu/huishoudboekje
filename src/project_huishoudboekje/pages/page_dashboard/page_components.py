
import plotly.express as px

from dash import html, dcc, dash_table

from project_huishoudboekje.config import TableSettings


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
                 'backgroundColor': px.colors.qualitative.Set2[2], 'color': 'white'},
                {'if': {'state': 'selected', 'row_index': 'odd'},
                 'backgroundColor': 'rgb(220, 220, 220)',
                 "border": "0px",
                 },
                {'if': {'state': 'selected', 'row_index': 'even'},
                 'backgroundColor': 'white',
                 "border": "0px",
                 }
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
                 'backgroundColor': px.colors.qualitative.Set2[2], 'color': 'white'},
                {'if': {'state': 'selected', 'row_index': 'odd'},
                 'backgroundColor': 'rgb(220, 220, 220)',
                 "border": "0px",
                 },
                {'if': {'state': 'selected', 'row_index': 'even'},
                 'backgroundColor': 'white',
                 "border": "0px",
                 }
            ],
            style_header={'backgroundColor': px.colors.qualitative.Dark2[2], 'fontWeight': 'bold', 'color': 'white'},
        ),
    ], style={'height': '25%', 'margin-left': '4px', 'margin-right': '4px', 'margin-top': '4px'})
