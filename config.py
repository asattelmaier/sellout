from pathlib import Path
import json


class Config:
    """Holds the configuration."""
    config_file = ""
    autthoken = ""

    def __init__(self, config_file):
        self.config_file = Path(config_file)
        self.parse_config_file()

    def parse_config_file(self):
        with self.config_file.open(encoding='utf-8') as config_file:
            config = json.load(config_file)

        self.autthoken = config["AUTHTOKEN"]
