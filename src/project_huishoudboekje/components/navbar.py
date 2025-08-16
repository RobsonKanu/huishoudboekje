
import plotly.express as px
import dash_bootstrap_components as dbc

from dash import html

# navigation bar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(dbc.Row(
                [dbc.Col(dbc.NavbarBrand("Huidhoudboekje Rob & Anne Schuitemaker", className="ms-2"))],
                align="center", className="g-0"), href="/", style={"textDecoration": "none"}
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
