# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
