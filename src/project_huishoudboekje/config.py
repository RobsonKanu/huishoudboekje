
from pathlib import Path
from dash.dash_table.Format import Format, Group, Symbol, Scheme

import dash_bootstrap_components as dbc

class GeneralSettings(object):

    project_path = Path(r'C:\Users\robsc\Documents\Python\Huishoudboekje')

    year_selected = 2024

    file_plaatsnaam = 'Woonplaatsen_in_Nederland_2020_07062022_225527'

class AppSettings(object):

    style_sheet = [dbc.themes.UNITED]

class TransactionSettings(object):

    long_iban = '[A-Z][A-Z][0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] ' + \
                '[0-9][0-9][0-9][0-9] [0-9][0-9] '
    nl_iban = '[A-Z][A-Z][0-9][0-9] [A-Z][A-Z][A-Z][A-Z] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9] '
    lu_iban = 'LU[0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] '
    be_iban = 'BE[0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] [0-9][0-9][0-9][0-9] '

    rgx_trans = '[0-9][0-9]-[0-9][0-9] [a-z][a-z].+?(?=Verwerkingsdatum: [0-9][0-9]-[0-9][0-9]-202[0-9])'

class TableSettings(object):

    euro_format = Format(precision=2,
                         group=Group.yes,
                         groups=3,
                         group_delimiter=" ",
                         scheme=Scheme.fixed,
                         symbol=Symbol.yes,
                         symbol_prefix=u'€ '
                         )