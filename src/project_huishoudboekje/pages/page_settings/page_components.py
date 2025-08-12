
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import html

modal_no_selection = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalBody(
                    'Geen bestand geselecteerd.'
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button("Close", id="no-selection-close", n_clicks=0),
                    ])
                ),
            ],
            id="modal-no-selection",
            is_open=False,
        ),
    ]
)

modal_remove_file = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalBody(
                    'Wil je de geselecteerde bestanden verwijderen?'
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button("Yes", id="yes-remove-file", n_clicks=0),
                        dbc.Button("No", id="no-remove-file", className="ms-auto", n_clicks=0)
                    ])
                ),
            ],
            id="modal-remove-file",
            is_open=False,
        ),
    ]
)

modal_remove = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalBody(
                    'Wil je deze categorie verwijderen?'
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button("Yes", id="yes-remove", n_clicks=0),
                        dbc.Button("No", id="no-remove", className="ms-auto", n_clicks=0)
                    ])
                ),
            ],
            id="modal-remove",
            is_open=False,
        ),
    ]
)

modal_edit = html.Div(
    [
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Header")),
                dbc.ModalBody(
                    html.Div([
                        html.Div(['Group', dbc.Input(id='group-edit')]),
                        html.Div(['Category', dbc.Input(id='category-edit')]),
                        html.Div(['Start', dbc.Input(id='startyear-edit')]),
                        html.Div(['End', dbc.Input(id='endyear-edit')])
                    ])
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button("Submit", id="submit-cat-edit", n_clicks=0),
                        dbc.Button("Close", id="close-edit", className="ms-auto", n_clicks=0)
                    ])
                ),
            ],
            id="modal-edit",
            is_open=False,
        ),
    ]
)

modal_add_category = html.Div(
    [
        dbc.Button("Add category", id="open", n_clicks=0,
                   style={'background-color': px.colors.qualitative.Dark2[2],
                          'border-width': '0px',
                          'textAlign': 'left',
                          'margin-top': '10px'}),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Header")),
                dbc.ModalBody(
                    html.Div([
                        html.Div(['Group', dbc.Input(id='group')]),
                        html.Div(['Category', dbc.Input(id='category')]),
                        html.Div(['Start', dbc.Input(id='startyear')]),
                        html.Div(['End', dbc.Input(id='endyear')])
                    ])
                ),
                dbc.ModalFooter(
                    html.Div([
                        dbc.Button("Submit", id="submit-cat", n_clicks=0),
                        dbc.Button("Close", id="close", className="ms-auto", n_clicks=0)
                    ])
                ),
            ],
            id="modal",
            is_open=False,
        ),
    ]
)

