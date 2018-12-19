import datetime as dt
import bs4 as bs
import pickle
import requests
from pathlib import Path
import quandl


class Dax:
    """Holds all information regarding to DAX"""
    TICKERS_URL = 'https://en.wikipedia.org/wiki/DAX'
    tickers = []
    authtoken = ""

    def __init__(self, authtoken):
        self.authtoken = authtoken
        self.load_saved_tickers()

    def get_tickers(self):
        return self.tickers

    def save_tickers(self):
        response = requests.get(self.TICKERS_URL)
        soup = bs.BeautifulSoup(response.text, 'lxml')
        tickers_table = soup.find('table', {'class': 'wikitable sortable'})

        self.tickers = []

        for row in tickers_table.findAll('tr')[1:]:
            ticker = row.findAll('a', {'class', 'external text'})[0].text
            self.tickers.append(ticker)

        with open('dax_tickers.pickle', 'wb') as f:
            pickle.dump(self.tickers, f)

    def load_saved_tickers(self):
        with open('dax_tickers.pickle', 'rb') as f:
            self.tickers = pickle.load(f)

    def get_ticker_data(self):
        stock_data_path = Path('stock_data')
        ticker_file_suffix = '.csv'
        start_date = dt.datetime(2015, 1, 1)
        end_date = dt.datetime.now()

        if not stock_data_path.exists():
            stock_data_path.mkdir()

        for ticker in self.tickers:
            ticker_file = stock_data_path / (ticker + ticker_file_suffix)

            if not ticker_file.exists():
                df = quandl.get('FSE/DBK_X', authtoken=self.authtoken, ticker=ticker, start_date=start_date,
                                end_date=end_date)

                df.reset_index(inplace=True)
                df.set_index('Date', inplace=True)

                df.to_csv(ticker_file)
            else:
                print('Already have {}'.format(ticker_file))
