
import plotly.express as px

from dash import html, dcc, dash_table
from dash.dash_table import FormatTemplate

# from project_huishoudboekje.components.navbar import navbar
from project_huishoudboekje.utils.graphs import (
    graph_total, graph_groups, graph_total_delta, graph_groups_delta
)
# from project_huishoudboekje.app import df_analysis, df_budget
from project_huishoudboekje.config import TableSettings


def style_html_div(width):
    return {
        'width': width,
        'backgroundColor': px.colors.qualitative.Pastel2[2],
        'padding': '5px',
        'margin-left': '20px',
        'margin-right': '20px',
        'textAlign': 'center'
    }


style_header ={
    'width': '130px',
    'height': '35px',
    'padding-top': '7px',
    'padding-left': '7px',
    'textAlign': 'center',
    'font-family': 'sans-serif',
    'font-style': 'normal'
}

width_figures = '450px'


def create_layout(navbar, df_budget, df_analysis):
    fig_totals_actual = graph_total(df_analysis, 'Actual')
    fig_groups_actual = graph_groups(df_analysis, 'Actual')
    fig_groups_budget = graph_groups(df_budget, 'Budget')
    fig_totals_budget = graph_total(df_budget, 'Budget')

    fig_totals_delta = graph_total_delta(df_budget, df_analysis)
    fig_groups_delta = graph_groups_delta(df_budget, df_analysis)

    return html.Div([
        navbar,
        html.Br(),
        html.Div([
            html.Div(
                [html.I("Total income and expenses per month",
                        style={'font-family': 'sans-serif', 'font-style': 'normal'})],
                style=style_html_div('29%')),
            html.Div(
                [html.I("Totals by expense group", style=style_header)],
                style=style_html_div('29%')),
            html.Div(
                [html.I("Comparison per category", style=style_header)],
                style=style_html_div('40%'))],
            style={'display': 'flex'}
        ),
        html.Br(),
        html.Div([
            html.Div([
                dcc.Graph(id='total-graph', figure=fig_totals_actual, style={'width': width_figures, 'height': '25vh'}),
                dcc.Graph(id='total-graph', figure=fig_totals_budget, style={'width': width_figures, 'height': '25vh'}),
                dcc.Graph(id='total-graph', figure=fig_totals_delta, style={'width': width_figures, 'height': '25vh'})
            ], style={'width': '29%', 'margin-left': '10px', 'margin-right': '0px'}),
            html.Div([
                dcc.Graph(id='group-graph', figure=fig_groups_actual, style={'width': width_figures, 'height': '25vh'}),
                dcc.Graph(id='group-graph', figure=fig_groups_budget, style={'width': width_figures, 'height': '25vh'}),
                dcc.Graph(id='group-graph', figure=fig_groups_delta, style={'width': width_figures, 'height': '25vh'})
            ], style={'width': '29%', 'margin-left': '10px', 'margin-right': '0px'}),
            html.Div([
                html.Div([
                    html.I("Select view: ", style=style_header),
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
