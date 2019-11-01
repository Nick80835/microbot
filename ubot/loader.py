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

import glob
from importlib import import_module
from os.path import basename, dirname, isfile
from re import escape

from telethon import events


class Loader():
    def __init__(self, client, cmd_prefix, logger):
        self.loaded_modules = []
        self.all_modules = []
        self.client = client
        self.cmd_prefix = cmd_prefix or '.'
        self.logger = logger
        self.botversion = "0.1.0"

    def load_all_modules(self):
        self._find_all_modules()

        for module_name in self.all_modules:
            self.loaded_modules.append(import_module("ubot.modules." + module_name))

    def add(self, **args):
        prefix = escape(self.cmd_prefix)
        args['outgoing'] = True

        if args.get('pattern', None) is not None:
            args['pattern'] = f"(?is)^{prefix}{args['pattern']}(?: |$)(.*)"

        def decorator(func):
            async def wrapper(event):
                try:
                    return await func(event)
                except Exception as exception:
                    self.logger.warn(f"{func.__name__} - {exception}")
                    await event.reply(f"`An error occurred in {func.__name__}: {exception}`")

            self.client.add_event_handler(wrapper, events.NewMessage(**args))
            return wrapper
        return decorator

    def _find_all_modules(self):
        mod_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = [
            basename(f)[:-3] for f in mod_paths
            if isfile(f) and f.endswith(".py")
        ]
