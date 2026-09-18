
import uuid
import pandas as pd

from rapidfuzz import process, fuzz

from project_huishoudboekje.config import GeneralSettings as GenSet
from project_huishoudboekje.prep_utils import check_previous_month, find_most_likely_category
from project_huishoudboekje.database import read_sql_table_cats, read_sql_table_transactions


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

        return df


    def assign_category(self, df):

        df_proc = read_sql_table_transactions(year=GenSet.year_selected, test_par=GenSet.test_par)

        for idx in df.index:

            if df.loc[idx, 'CATEGORY'] == 'Niet-gecategoriseerd':
                party = df.loc[idx, 'PARTY']
                amount = df.loc[idx, 'AMOUNT']
                fin_type = df.loc[idx, 'FINANCIAL_TYPE']

                # rapidfuzz score_cutoff is on a 0-100 scale; 60 is equivalent to difflib's
                # previous cutoff=.6. Same "top 3 closest matches" semantics as before.
                matches = process.extract(party, df_proc['PARTY'], scorer=fuzz.ratio, limit=3, score_cutoff=60)

                if matches:
                    matched_parties = [m[0] for m in matches]
                    df_match = df_proc.loc[df_proc.PARTY.isin(matched_parties), :]

                    df, success = check_previous_month(df_match, df, idx, amount, fin_type)

                    if not success:
                        df = find_most_likely_category(df_match, df, idx, amount, fin_type)

        return df
