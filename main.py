from config import Config
from dax import Dax
from ticker_evaluator import TickerEvaluator

if __name__ == '__main__':
    config_file = 'config.json'
    config = Config.create_config(config_file)

    dax = Dax.create_dax(config.authtoken)
    dax.get_ticker_data()
    dax.compile_data()

    future_days = 7
    tickers = ['ADS']
    ticker_evaluator = TickerEvaluator(dax.table, tickers, future_days)

    ticker_evaluator.evaluate()