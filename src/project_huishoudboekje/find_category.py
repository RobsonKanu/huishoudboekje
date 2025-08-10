
import uuid
import difflib
import pandas as pd

from project_huishoudboekje.config import GeneralSettings as GenSet
from project_huishoudboekje.prep_utils import check_previous_month, find_most_likely_category
from project_huishoudboekje.database import read_sql_table_cats


class FindCategory(object):

    def run(self, df, source):

        df_categories = read_sql_table_cats(to_records=False, fill_nan_end_year=True).rename(
            columns={'grouplevel': 'GROUP', 'category': 'CATEGORY'})

        # Add unique ID for each transaction
        df['TRANS_ID'] = [uuid.uuid4() for _ in range(len(df.index))]

        df = df.assign(
            SOURCE=source,
            CATEGORY='Niet-gecategoriseerd').set_index('TRANS_ID')

        df = self.assign_category(df)

        df = df.reset_index().merge(
            df_categories, how='left', left_on='CATEGORY', right_on='CATEGORY').rename(
            columns={'index': 'TRANS_ID'})

        # select merged categories that have a valid period
        df = df[((df['CATEGORY'] == 'Niet-gecategoriseerd') | ((df['DATE'].dt.year >= df['begin_year']) & (
                df['DATE'].dt.year <= df['end_year'])))].drop(columns=['begin_year', 'end_year']).copy()

        return df.set_index('TRANS_ID').reindex(
            columns=['DATE', 'SOURCE', 'TRANSACTION_TYPE', 'FINANCIAL_TYPE', 'PARTY', 'AMOUNT',
                     'CATEGORY', 'ANALYSE_IND', 'GROUP'])

    def assign_category(self, df):

        df_proc = pd.read_excel(GenSet.project_path / f'data/processed/transactions{GenSet.test_par}.xlsx')

        for idx in df.index:

            if df.loc[idx, 'CATEGORY'] == 'Niet-gecategoriseerd':
                party = df.loc[idx, 'PARTY']
                amount = df.loc[idx, 'AMOUNT']
                fin_type = df.loc[idx, 'FINANCIAL_TYPE']

                matches = difflib.get_close_matches(party, df_proc['PARTY'], n=3, cutoff=.6)

                if matches:
                    df_match = df_proc.loc[df_proc.PARTY.isin(matches), :]

                    df, success = check_previous_month(df_match, df, idx, amount, fin_type)

                    if not success:
                        df = find_most_likely_category(df_match, df, idx, amount, fin_type)

        return df
