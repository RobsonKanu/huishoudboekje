
import os

from project_huishoudboekje.config import GeneralSettings
from project_huishoudboekje.read_rabo import ReadRabo
from project_huishoudboekje.read_asn import ReadAsn
from project_huishoudboekje.find_category import FindCategory
from project_huishoudboekje.store_results import StoreResults
from project_huishoudboekje.app import App

def run():
    filenames_rabobank = next(os.walk(GeneralSettings.project_path / f'data/Rabobank'), (None, None, []))[2]
    filenames_asn_bank = next(os.walk(GeneralSettings.project_path / f'data/ASN Bank'), (None, None, []))[2]

    if filenames_rabobank:
        df = ReadRabo().run(filenames_rabobank)
        df = FindCategory().run(df, 'Rabobank')
        StoreResults().run(df)

    if filenames_asn_bank:
        df = ReadAsn().run(filenames_asn_bank)
        df = FindCategory().run(df, 'ASN Bank')
        StoreResults().run(df)

    App().run()


if __name__ == '__main__':
    run()
