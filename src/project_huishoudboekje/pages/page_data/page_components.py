
import plotly.express as px

from dash import html, dash_table
from dash.dash_table.Format import Format

from project_huishoudboekje.config import TableSettings


button_style = {
    'backgroundColor': px.colors.qualitative.Pastel2[2],
    'font-family': 'sans-serif',
    'font-size': '14px',
    'border': 'none',
    'margin-left': '2px',
    'margin-right': '2px'
}


def create_dash_table_data(df_data, df_categories):
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
            data=df_data.to_dict('records'),
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
