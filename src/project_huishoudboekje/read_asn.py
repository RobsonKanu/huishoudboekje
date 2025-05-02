
from project_huishoudboekje.config import GeneralSettings

import pandas as pd

from shutil import move


class ReadAsn(object):

    def run(self, list_files):
        list_out = []

        for file in list_files:
            df = pd.read_csv(GeneralSettings.project_path / f'data/ASN Bank/{file}', header=None)

            list_out.append(df)

            move(GeneralSettings.project_path / f'data/ASN Bank/{file}',
                 GeneralSettings.project_path / f'data/archive/{file}')

        df_full = pd.concat(list_out, ignore_index=True)

        df_out = self.prepare_data_asn(df_full)

        return df_out


    def prepare_data_asn(self, df):

        # Date
        df['DATE'] = pd.to_datetime(df.iloc[:, 0], format='%d-%m-%Y')

        # Financial type
        df['FINANCIAL_TYPE'] = df.iloc[:, 10].apply(lambda x: 'credit' if x > 0 else 'debet')

        # Amount
        df['AMOUNT'] = df.iloc[:, 10].abs()

        # Transaction type
        df['TRANSACTION_TYPE'] = df.iloc[:, 14]

        # Analysis indicator
        df['ANALYSE_IND'] = df['TRANSACTION_TYPE'].apply(lambda x: 0 if x == 'NGM' else 1)

        # Party
        df['PARTY'] = df.iloc[:, 3].astype(str) + ' - ' + df.iloc[:, 17].str[1:-1].str.split().str[:3].str.join(sep=" ")
        df['PARTY'] = df['PARTY'].str.replace('nan - ', '').fillna('Onbekend')

        return df[['DATE', 'FINANCIAL_TYPE', 'TRANSACTION_TYPE', 'PARTY', 'AMOUNT', 'ANALYSE_IND']]
