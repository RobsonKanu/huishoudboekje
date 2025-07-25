
from pathlib import Path
from dash.dash_table.Format import Format, Group, Symbol, Scheme

import dash_bootstrap_components as dbc


class GeneralSettings(object):

    project_path = Path(r'C:\Users\robsc\Documents\Analyse\Huishoudboekje')

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


class FigureSettings(object):

    group_colors = {
        'Aankopen': '#636EFA',
        'Auto en vervoer': '#EF553B',
        'Giften': '#00CC96',
        'Leven en entertainment': '#AB63FA',
        'Overig': '#FFA15A',
        'Verzekeringen': '#19D3F3',
        'Verzorging en gezondheid': '#FF6692',
        # 'Woning': '#B6E880',
        'Woonlasten': '#B6E880'
    }
