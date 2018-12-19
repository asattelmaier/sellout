from pathlib import Path
import json


class Config:
    """Holds the configuration."""
    config_file = ""
    authtoken = ""

    def __init__(self, config_file):
        self.config_file = Path(config_file)

    def parse_config_file(self):
        with self.config_file.open(encoding='utf-8') as config_file:
            config = json.load(config_file)

        self.authtoken = config["AUTHTOKEN"]

    @staticmethod
    def create_config(config_file):
        config = Config(config_file)
        config.parse_config_file()
        return config
