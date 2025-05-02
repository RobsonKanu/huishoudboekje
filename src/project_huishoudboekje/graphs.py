
import plotly.express as px


def graph_group_month(df_analysis):

    df_stack = df_analysis[df_analysis.GROUP != 'Inkomsten'].groupby(
        ['YEAR_MONTH', 'GROUP'])['AMOUNT_NW'].sum().reset_index()

    df_stack['Percentage'] = df_analysis[df_analysis.GROUP != 'Inkomsten'].groupby(
        ['YEAR_MONTH', 'GROUP'])['AMOUNT_NW'].sum().groupby(level=0).apply(
        lambda x: x / float(x.sum())).values
    df_stack.columns = ['Month', 'Group', 'Amount', 'Percentage']

    fig = px.bar(df_stack, x='Month', y='Percentage', color='Group',
                 category_orders={
                     'Group': ['Aankopen', 'Auto en vervoer', 'Giften', 'Leven en entertainment', 'Overig',
                               'Verzekeringen', 'Verzorging en gezondheid', 'Woning']},
                 color_discrete_map={'Aankopen': '#636EFA',
                                     'Auto en vervoer': '#EF553B',
                                     'Giften': '#00CC96',
                                     'Leven en entertainment': '#AB63FA',
                                     'Overig': '#FFA15A',
                                     'Verzekeringen': '#19D3F3',
                                     'Verzorging en gezondheid': '#FF6692',
                                     'Woning': '#B6E880'}
                 )
    fig.update_layout(title="Expense distribution per month",
                      title_y=1,
                      xaxis_title=None,
                      yaxis_title=None,
                      xaxis={'type': 'category'},
                      yaxis={'tickformat': ',.0%'},
                      margin=dict(l=20, r=20, t=30, b=20),
                      legend_title_text="",
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=1.02,
                          xanchor="left",
                          x=0
                      )
                      )

    return fig


def graph_groups(df_analysis, title_name):

    df_stack = df_analysis[df_analysis.GROUP != 'Inkomsten'].groupby(['GROUP'])[
        'AMOUNT_NW'].sum().reset_index().rename(
        columns={'GROUP': 'Group', 'AMOUNT_NW': 'Amount'})
    fig = px.bar(df_stack, x='Group', y='Amount',
                 color='Group',
                 category_orders={
                     'Group': ['Aankopen', 'Auto en vervoer', 'Giften', 'Leven en entertainment', 'Overig',
                               'Verzekeringen', 'Verzorging en gezondheid', 'Woning']},
                 color_discrete_map={'Aankopen': '#636EFA',
                                     'Auto en vervoer': '#EF553B',
                                     'Giften': '#00CC96',
                                     'Leven en entertainment': '#AB63FA',
                                     'Overig': '#FFA15A',
                                     'Verzekeringen': '#19D3F3',
                                     'Verzorging en gezondheid': '#FF6692',
                                     'Woning': '#B6E880'})

    fig.update_layout(title=title_name, showlegend=False, yaxis_title=None, xaxis={'type': 'category'},
                      xaxis_title=None, margin=dict(l=20, r=20, t=30, b=20))
    fig.update_xaxes(showticklabels=False)

    return fig


def graph_total(df_analysis, title_name):

    df_stack = df_analysis.groupby(['YEAR_MONTH', 'INCOME_IND'])['AMOUNT_NW'].sum().reset_index().rename(
        columns={'AMOUNT_NW': 'Amount'})

    fig = px.bar(df_stack, x='YEAR_MONTH', y='Amount', color='INCOME_IND', barmode='group',
                  color_discrete_sequence=["#B6E880", "#EF553B"])
    fig.update_layout(title=title_name, showlegend=False, yaxis_title=None, xaxis={'type': 'category'},
                      xaxis_title=None, margin=dict(l=20, r=20, t=30, b=20))

    return fig


def graph_total_delta(df_budget, df_analysis):

    df_analysis_stack = df_analysis.groupby(['YEAR_MONTH', 'INCOME_IND'])['AMOUNT_NW'].sum().reset_index().rename(
        columns={'AMOUNT_NW': 'ACTUAL'})
    df_budget_stack = df_budget.groupby(['YEAR_MONTH', 'INCOME_IND'])['AMOUNT_NW'].sum().reset_index().rename(
        columns={'AMOUNT_NW': 'BUDGET'})

    df_total_stack = df_budget_stack.merge(df_analysis_stack, on=['YEAR_MONTH', 'INCOME_IND'], how='left').fillna(0)
    df_total_stack['DELTA'] = df_total_stack.apply(
        lambda x: x['BUDGET'] - x['ACTUAL'] if x['INCOME_IND'] == 'Uitgaven' else x['ACTUAL'] - x['BUDGET'],
        axis=1)

    fig = px.bar(df_total_stack, x='YEAR_MONTH', y='DELTA', color='INCOME_IND', barmode='group',
                 color_discrete_sequence=["#B6E880", "#EF553B"])
    fig.add_hline(y=0)
    fig.update_layout(title='Delta', showlegend=False, yaxis_title=None, xaxis={'type': 'category'},
                      xaxis_title=None, margin=dict(l=20, r=20, t=30, b=20))

    return fig


def graph_groups_delta(df_budget, df_analysis):

    df_analysis_stack = df_analysis[df_analysis.GROUP != 'Inkomsten'].groupby(['GROUP'])[
        'AMOUNT_NW'].sum().reset_index().rename(
        columns={'GROUP': 'Group', 'AMOUNT_NW': 'ACTUAL'})
    df_budget_stack = df_budget[df_budget.GROUP != 'Inkomsten'].groupby(['GROUP'])[
        'AMOUNT_NW'].sum().reset_index().rename(
        columns={'GROUP': 'Group', 'AMOUNT_NW': 'BUDGET'})

    df_total_stack = df_budget_stack.merge(df_analysis_stack, on=['Group'], how='left').fillna(0)
    df_total_stack['DELTA'] = df_total_stack['BUDGET'] - df_total_stack['ACTUAL']

    df_total_stack['COLORMAP'] = df_total_stack['DELTA'].apply(lambda x: "#B6E880" if x > 0 else "#EF553B")

    fig = px.bar(df_total_stack, x='Group', y='DELTA',
                 #color='Group',
                 category_orders={
                     'Group': ['Aankopen', 'Auto en vervoer', 'Giften', 'Leven en entertainment', 'Overig',
                               'Verzekeringen', 'Verzorging en gezondheid', 'Woning']},
                 color_discrete_map={'Aankopen': '#636EFA',
                                     'Auto en vervoer': '#EF553B',
                                     'Giften': '#00CC96',
                                     'Leven en entertainment': '#AB63FA',
                                     'Overig': '#FFA15A',
                                     'Verzekeringen': '#19D3F3',
                                     'Verzorging en gezondheid': '#FF6692',
                                     'Woning': '#B6E880'})

    fig.update_traces(marker={'color': df_total_stack['COLORMAP']}, selector=dict(type='bar'))

    fig.add_hline(y=0)

    fig.update_layout(title='Delta', yaxis_title=None,
                      xaxis_title=None, margin=dict(l=20, r=20, t=30, b=20),
                      xaxis={'type': 'category'},
                      legend_title_text="",
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=1.02,
                          xanchor="left",
                          x=0
                      )
                      )
    fig.update_xaxes(showticklabels=False)

    return fig
