import re
import pandas as pd

from PyPDF2 import PdfReader
from datetime import datetime

from project_huishoudboekje.utils import string_to_float
from project_huishoudboekje.config import GeneralSettings, TransactionSettings


class ReadRaboPdf(object):

    def run(self, list_files):

        list_out = []

        for file in list_files:

            reader = PdfReader(str(GeneralSettings.project_path / f'data/Rabobank (pdf)/{file}'))

            dict_account, list_trans = self.get_all_transactions(reader)

            df = self.process_transactions(list_trans)

            self._validate_results(dict_account, df)

            list_out.append(df)

        df_out = pd.concat(list_out, ignore_index=True)

        df_out['DATE'] = pd.to_datetime(df_out['DATE'])

        df_out['ANALYSE_IND'] = df_out['TRANSACTION_TYPE'].apply(lambda x: 0 if x == 'tb' else 1)

        return df_out

    def get_header(self, text):

        string_name = 'Bedrag bij (credit)\n'
        header_num = text.find(string_name)

        return text[:(header_num + len(string_name))]

    def get_body(self, text, header):

        return text.replace('\nCR = tegoed\nD   = tekort\n', '').replace(header, '')

    def get_all_transactions(self, reader):

        num_of_pages = len(reader.pages)

        list_bodies = []

        for num, page in enumerate(reader.pages):

            text = page.extract_text()
            header = self.get_header(text)

            if num == 0:
                dict_account = self.get_account_values(header.split('\n'))

            body = self.get_body(text, header)

            list_bodies.append(body)

        all_trans = '\n'.join(list_bodies)

        trans_no_footer = all_trans[:all_trans.find('\nac = acceptgiro')]

        trans_str = ' '.join(trans_no_footer.split('\n'))

        trans_list = re.findall(TransactionSettings.rgx_trans, trans_str)

        return dict_account, trans_list

    def get_account_values(self, text):
        """Only for first page"""

        account_values = ['Beginsaldo', 'Eindsaldo', 'Totaal afgeschreven', 'Totaal bijgeschreven']
        dict_account = {}

        for num, val in enumerate(text):
            if val in account_values:
                dict_account[val] = string_to_float(text[num+1])

        return dict_account

    def process_transactions(self, list_trans):

        dict_trans = {}

        for no, trans in enumerate(list_trans):

            # Date
            date = datetime(2022, int(trans[3:5]), int(trans[:2])) # todo: fix year element

            # Transaction type
            trans_type = trans[6:8]

            # Transaction amount and party
            if trans_type in ['ei', 'id', 'cb', 'sb', 'bg', 'tb', 'bv', 'te', 'kh']:
                amount, party = self.get_transaction_info_iban(trans)
            elif trans_type in ['bc', 'db', 'cc', 'ba', 'ga']:
                amount, party = self.get_transaction_info_other(trans)
            else:
                raise ValueError(f'Unknown transaction type={trans_type}')

            # Credit/debet transaction
            if trans_type in ['cb', 'sb', 'tb', 'ba', 'bv', 'te', 'kh']:
                fin_type = 'credit'
            else:
                fin_type = 'debet'

            dict_trans[no] = {
                'DATE': date, 'TRANSACTION_TYPE': trans_type, 'FINANCIAL_TYPE': fin_type, 'PARTY': party,
                'AMOUNT': string_to_float(amount)
            }

        return pd.DataFrame.from_dict(dict_trans, orient='index')

    def get_transaction_info_iban(self, trans):

        # If IBAN is longer than normal, look one word further
        if re.search(TransactionSettings.long_iban, trans):
            pos = 1
        elif re.search(TransactionSettings.nl_iban, trans):
            pos = 0
        elif re.search(TransactionSettings.be_iban, trans):
            pos = -1
        elif re.search(TransactionSettings.lu_iban, trans):
            pos = 0
        else:

            print(f'Unable to get transaction information from transaction={trans}. Try other method...')

            amount, party = self.get_transaction_info_other(trans)

            return amount, party

        amount = trans.split()[7+pos]
        party = ' '.join(trans.split()[(8+pos):(11+pos)]) # todo: taken 3 words, but parties may have different lengths

        return amount, party

    def get_transaction_info_other(self, trans):

        # Find the transaction amount and get everything in front of it
        rgx = re.search('([^\s]*?),[0-9][0-9]', trans)

        # Transaction amount
        amount = rgx.group(0)

        # Party starts from position 9 and ends at the position found in the regex-search
        party = trans[9:(rgx.span(0)[0] - 1)]

        return amount, party

    def _validate_results(self, dict_account, df):

        df_tot = df.groupby('FINANCIAL_TYPE')['AMOUNT'].sum()

        account_cr_sum = dict_account['Totaal bijgeschreven']
        account_db_sum = dict_account['Totaal afgeschreven']
        trans_cr_sum = df_tot['credit'].round(2)
        trans_db_sum = df_tot['debet'].round(2)

        if account_cr_sum != trans_cr_sum:
            raise ValueError(
                f'Total credit amount is not equal. Account summary={account_cr_sum}. Transaction sum={trans_cr_sum}.')

        if account_db_sum != trans_db_sum:
            raise ValueError(
                f'Total debet amount is not equal. Account summary={account_db_sum}. Transaction sum={trans_db_sum}.')


class ReadRabo(object):

    def run(self, list_files):
        list_out = []

        for file in list_files:
            df = pd.read_csv(GeneralSettings.project_path / f'data/Rabobank/{file}', encoding='latin-1')

            list_out.append(df)

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
