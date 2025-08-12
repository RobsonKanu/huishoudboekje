
from dash import html

from project_huishoudboekje.utils.graphs import (
    graph_group_month, graph_groups, graph_total
)
from project_huishoudboekje.pages.page_dashboard.page_components import (
    get_page_1_graphs, get_page_1_selector, get_page_1_table_budget, get_page_1_table_actuals
)


def create_layout(navbar, df_analysis, month_names):
    # Get all unique groups
    available_groups = list(df_analysis[df_analysis.CATEGORY != 'Niet-gecategoriseerd'].GROUP.unique())

    # Get graphs
    fig_group_month = graph_group_month(df_analysis)
    fig_groups = graph_groups(df_analysis, 'Totals by expense group')
    fig_totals = graph_total(df_analysis, "Total income and expenses per month")

    return html.Div([
        navbar,
        get_page_1_graphs(fig_totals, fig_groups, fig_group_month),
        get_page_1_selector(available_groups),
        get_page_1_table_actuals(month_names),
        get_page_1_table_budget(month_names)
    ])
