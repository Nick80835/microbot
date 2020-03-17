# SPDX-License-Identifier: GPL-2.0-or-later

from configparser import SafeConfigParser


class Settings():
    def __init__(self):
        self.config = SafeConfigParser()
        self.config.read("settings.ini")

    def get_config(self, key):
        return self.config.get("DEFAULT", key, fallback=None)

    def get_bool(self, key):
        return bool(self.config.get("DEFAULT", key, fallback=False) == "True")

    def set_config(self, key, value):
        self.config.set("DEFAULT", key, value)

        with open('settings.ini', 'w') as config_file:
            self.config.write(config_file)
            config_file.close()
