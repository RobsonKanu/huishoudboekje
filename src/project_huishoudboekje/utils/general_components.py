from dash import html


def get_label_style(options_list):
    options = []
    for i in options_list:
        options.append(
            {'label': html.Div(i, style={'color': 'black', 'fontSize': 18,
                                         'padding-left': '10px',
                                         'display': "inline-block"}),
             'value': i}
        )

    return options
