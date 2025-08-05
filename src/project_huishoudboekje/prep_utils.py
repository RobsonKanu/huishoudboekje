
import pandas as pd

from dateutil.relativedelta import relativedelta


def string_to_float(string):

    try:
        return float(string.split(' ')[0].replace('.', '').replace(',', '.'))
    except:
        raise ValueError(f'Unable to convert string={string} to float.')


def check_previous_month(df, df_new, idx, amount, fin_type):
    previous_date = df_new.loc[idx, 'DATE'] - relativedelta(months=1)

    df_sel = df.loc[(df.DATE.dt.year == previous_date.year) & (df.DATE.dt.month == previous_date.month)]

    if df_sel.empty:
        return df_new, False

    date_sel = df_sel['DATE'].iloc[0].day

    if df_sel.AMOUNT.sum() == amount and df_sel['FINANCIAL_TYPE'].iloc[0] == fin_type and \
            max(previous_date.day - 4, 1) <= date_sel <= max(previous_date.day + 4, 31):
        list_cats = df_sel[['AMOUNT', 'CATEGORY']].values.tolist()

        if len(list_cats) > 1:
            df_new = pd.concat([df_new, pd.DataFrame([df_new.loc[idx]] * (len(list_cats) - 1))])

            df_new.loc[idx, ['AMOUNT', 'CATEGORY']] = list_cats
        else:
            df_new.loc[idx, 'CATEGORY'] = list_cats[0][1]

        success = True
    else:
        success = False

    return df_new, success


def find_most_likely_category(df_match, df, idx, amount, fin_type):
    df_sel = df_match.loc[df_match.FINANCIAL_TYPE == fin_type]

    if df_sel.empty:
        return df
    else:
        df.loc[idx, 'CATEGORY'] = df_sel.CATEGORY.value_counts().index[0]

        return df
