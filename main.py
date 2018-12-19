from dax import Dax
from config import Config

if __name__ == '__main__':
    config_file = 'config.json'
    config = Config.create_config(config_file)

    dax = Dax.create_dax(config.authtoken)
    dax.get_ticker_data()
    dax.compile_data()
