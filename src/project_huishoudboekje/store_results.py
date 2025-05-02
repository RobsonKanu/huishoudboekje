
import os
import pandas as pd
import shutil

from project_huishoudboekje.config import GeneralSettings


class StoreResults(object):

    # TODO: store input in processed folder
    def run(self, df):

        if os.path.exists(GeneralSettings.project_path / 'data/processed/transactions.xlsx'):
            df_old = pd.read_excel(GeneralSettings.project_path / 'data/processed/transactions.xlsx', index_col=0)

            df = pd.concat([df_old, df])

            shutil.copyfile(GeneralSettings.project_path / 'data/processed/transactions.xlsx',
                            GeneralSettings.project_path / 'data/processed/transactions_old.xlsx')

        df.to_excel(GeneralSettings.project_path / 'data/processed/transactions.xlsx')
