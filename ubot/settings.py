# SPDX-License-Identifier: GPL-2.0-or-later

from configparser import SafeConfigParser


class Settings():
    def __init__(self):
        self.config = SafeConfigParser()
        self.config.read("settings.ini")

    def get_config(self, key, default=None):
        return self.config.get("DEFAULT", key, fallback=default)

    def get_bool(self, key, default=False):
        return bool(self.config.get("DEFAULT", key, fallback=default) == "True")

    def set_config(self, key, value):
        self.config.set("DEFAULT", key, value)

        with open('settings.ini', 'w') as config_file:
            self.config.write(config_file)
            config_file.close()
