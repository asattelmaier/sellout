import datetime as dt
import bs4 as bs
import pickle
import requests
from pathlib import Path
import quandl
import pandas as pd


class Dax:
    """Holds all information regarding to DAX"""
    TICKERS_URL = 'https://en.wikipedia.org/wiki/DAX'
    TICKERS_FILE = Path('dax_tickers.pickle')
    STOCK_DATA_PATH = Path('stock_data')
    DAX_DATA_FILE = Path('dax_data.csv')
    TABLE_INDEX = 'Date'
    tickers = []
    ticker_file_suffix = '.csv'
    authtoken = ""

    def __init__(self, authtoken):
        self.authtoken = authtoken

    @staticmethod
    def create_dax(authtoken):
        dax = Dax(authtoken)
        dax.parse_tickers_file()

        return dax

    def save_tickers(self):
        response = requests.get(self.TICKERS_URL)
        soup = bs.BeautifulSoup(response.text, 'lxml')
        tickers_table = soup.find('table', {'class': 'wikitable sortable'})

        self.tickers = []

        for row in tickers_table.findAll('tr')[1:]:
            ticker = row.findAll('a', {'class', 'external text'})[0].text
            self.tickers.append(ticker)

        with self.TICKERS_FILE.open('wb') as f:
            pickle.dump(self.tickers, f)

    def parse_tickers_file(self):
        with self.TICKERS_FILE.open('rb') as tickers_file:
            self.tickers = pickle.load(tickers_file)

    def get_ticker_data(self):
        start_date = dt.datetime(2015, 1, 1)
        end_date = dt.datetime.now()

        if not self.STOCK_DATA_PATH.exists():
            self.STOCK_DATA_PATH.mkdir()

        for ticker in self.tickers:
            ticker_file = self.get_ticker_path(ticker)

            if not ticker_file.exists():
                df = quandl.get('FSE/DBK_X', authtoken=self.authtoken, ticker=ticker, start_date=start_date,
                                end_date=end_date)

                df = self.set_index_to_table(df)

                df.to_csv(ticker_file)
            else:
                print('Already have {}'.format(ticker_file))

    def compile_data(self):
        main_df = pd.DataFrame()

        for count, ticker in enumerate(self.tickers):
            ticker_file = self.get_ticker_path(ticker)
            df = pd.read_csv(ticker_file)

            df = self.set_index_to_table(df)

            df.rename(columns={'Close': ticker}, inplace=True)
            df = df[[ticker]]

            if main_df.empty:
                main_df = df
            else:
                main_df = main_df.join(df, how='outer')

            if count % 10 == 0:
                print(count)

        print(main_df.head())
        main_df.to_csv(self.DAX_DATA_FILE)

    def get_ticker_path(self, ticker):
        return self.STOCK_DATA_PATH / (ticker + self.ticker_file_suffix)

    def set_index_to_table(self, table):
        table.reset_index(inplace=True)
        table.set_index(self.TABLE_INDEX, inplace=True)

        return table
