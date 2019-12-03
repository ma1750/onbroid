import json

class Config():
    def __init__(self, config_file):
        with open(config_file) as f:
            self.config = json.load(f)

        self.token = self.config.get('token')
        self.prefix = self.config.get('prefix') or '$'