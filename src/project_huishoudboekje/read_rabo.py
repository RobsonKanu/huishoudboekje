import pandas as pd

from shutil import move

from project_huishoudboekje.config import GeneralSettings


class ReadRabo(object):

    def run(self, list_files):
        list_out = []

        for file in list_files:
            df = pd.read_csv(GeneralSettings.project_path / f'data/Rabobank/{file}', encoding='latin-1')

            list_out.append(df)

            move(GeneralSettings.project_path / f'data/Rabobank/{file}',
                 GeneralSettings.project_path / f'data/archive/{file}')

        df_full = pd.concat(list_out, ignore_index=True)

        df_out = self.prepare_data_rabo_csv(df_full)

        return df_out

    def prepare_data_rabo_csv(self, df):

        # Date
        df['DATE'] = pd.to_datetime(df['Datum'], format='%Y-%m-%d')

        # Amount
        df['AMOUNT_NO_ABS'] = df['Bedrag'].apply(lambda x: float(x.replace('+', '').replace(',', '.')))
        df['AMOUNT'] = df['AMOUNT_NO_ABS'].abs()

        # Financial type
        df['FINANCIAL_TYPE'] = df['AMOUNT_NO_ABS'].apply(lambda x: 'credit' if x > 0 else 'debet')

        # Analysis indicator
        df['ANALYSE_IND'] = df['Code'].apply(lambda x: 0 if x == 'tb' else 1)

        # Party
        df['PARTY'] = df['Naam tegenpartij'].astype(str) + ' - ' + df['Omschrijving-1'].str.split().str[:3].str.join(sep=" ")

        return df.rename(columns={'Code': 'TRANSACTION_TYPE'})[
            ['DATE', 'FINANCIAL_TYPE', 'TRANSACTION_TYPE', 'PARTY', 'AMOUNT', 'ANALYSE_IND']]
