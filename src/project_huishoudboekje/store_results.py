
import os
import pandas as pd
import shutil

from project_huishoudboekje.config import GeneralSettings as GenSet
from project_huishoudboekje.database import add_transactions_to_db


class StoreResults(object):

    def run(self, df):

        add_transactions_to_db(df, test_par=GenSet.test_par)

        # if os.path.exists(GenSet.project_path / f'data/processed/transactions{GenSet.test_par}.xlsx'):
        #     df_old = pd.read_excel(GenSet.project_path / f'data/processed/transactions{GenSet.test_par}.xlsx',
        #                            index_col=0)
        #
        #     df = pd.concat([df_old, df])
        #
        #     shutil.copyfile(GenSet.project_path / f'data/processed/transactions{GenSet.test_par}.xlsx',
        #                     GenSet.project_path / f'data/processed/transactions{GenSet.test_par}_old.xlsx')
        #
        # df.to_excel(GenSet.project_path / f'data/processed/transactions{GenSet.test_par}.xlsx')
