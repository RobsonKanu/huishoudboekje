
from pathlib import Path
from dash.dash_table.Format import Format, Group, Symbol, Scheme

import dash_bootstrap_components as dbc


class GeneralSettings(object):

    project_path = Path(r'C:\Users\robsc\Documents\Projecten\huishoudboekje')

    year_selected = 2025


class AppSettings(object):

    style_sheet = [dbc.themes.UNITED]


class TableSettings(object):

    euro_format = Format(precision=2,
                         group=Group.yes,
                         groups=3,
                         group_delimiter=" ",
                         scheme=Scheme.fixed,
                         symbol=Symbol.yes,
                         symbol_prefix=u'€ '
                         )
