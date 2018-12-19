from pathlib import Path
import json

from dax import Dax

if __name__ == '__main__':
    CONFIG_FILE = Path('config.json')
    with CONFIG_FILE.open(encoding='utf-8') as config_file:
        config = json.load(config_file)

    AUTHTOKEN = config["AUTHTOKEN"]

    dax = Dax(AUTHTOKEN)
    dax.get_ticker_data()
