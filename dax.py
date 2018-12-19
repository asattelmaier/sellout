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
    REMOTE_STOCK_DATA = 'FSE/DBK_X'
    STOCK_DATA_PATH = Path('stock_data')
    DAX_DATA_FILE = Path('dax_data.csv')
    TABLE_INDEX = 'Date'
    table = pd.DataFrame()
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
                remote_stock_table = quandl.get(self.REMOTE_STOCK_DATA, authtoken=self.authtoken, ticker=ticker,
                                                start_date=start_date,
                                                end_date=end_date)

                remote_stock_table = self.set_index_to_table(remote_stock_table)

                remote_stock_table.to_csv(ticker_file)
            else:
                print('Already have {}'.format(ticker_file))

    def compile_data(self):
        for count, ticker in enumerate(self.tickers):
            tickers_file = self.get_ticker_path(ticker)
            tickers_table = pd.read_csv(tickers_file)

            tickers_table = self.set_index_to_table(tickers_table)

            tickers_table.rename(columns={'Close': ticker}, inplace=True)
            tickers_table = tickers_table[[ticker]]

            self.append_to_data(tickers_table)

            if count % 10 == 0:
                print(count)

        print(self.table.head())
        self.write_data_to_file()

    def append_to_data(self, table):
        if self.table.empty:
            self.table = table
        else:
            self.table = self.table.join(table, how='outer')

    def write_data_to_file(self):
        self.table.to_csv(self.DAX_DATA_FILE)

    def get_ticker_path(self, ticker):
        return self.STOCK_DATA_PATH / (ticker + self.ticker_file_suffix)

    def set_index_to_table(self, table):
        table.reset_index(inplace=True)
        table.set_index(self.TABLE_INDEX, inplace=True)

        return table
