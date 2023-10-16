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
from importlib import import_module, reload
from os.path import basename, dirname, isfile
from re import escape

from telethon import events

from .command_handler import CommandHandler


class Loader():
    def __init__(self, client, logger, settings):
        self.loaded_modules = []
        self.all_modules = []
        self.client = client
        self.logger = logger
        self.settings = settings
        self.command_handler = CommandHandler(client, logger)
        self.botversion = "0.1.2"

    def load_all_modules(self):
        self._find_all_modules()

        for module_name in self.all_modules:
            self.loaded_modules.append(import_module("ubot.modules." + module_name))

    def reload_all_modules(self):
        self.command_handler.outgoing_commands = {}
        self.command_handler.incoming_commands = {}

        errors = ""

        for module in self.loaded_modules:
            try:
                reload(module)
            except Exception as exception:
                errors += f"`Error while reloading {module.__name__} -> {exception}\n\n`"
                raise exception

        return errors or None

    def add(self, **args):
        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        if args.get('noprefix', None):
            del args['noprefix']
            prefix = ''

        if not args.get('isfilter', False) and args.get('pattern', None) is not None:
            args['pattern'] = f"(?is)^{prefix}{args['pattern']}(?: |$)(.*)"
        else:
            del args['isfilter']
            args['pattern'] = f"(?is)(.*){args['pattern']}(.*)"

        def decorator(func):
            self.command_handler.incoming_commands[args['pattern']] = func

        return decorator

    def _find_all_modules(self):
        mod_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = [
            basename(f)[:-3] for f in mod_paths
            if isfile(f) and f.endswith(".py")
        ]

        system_index = self.all_modules.index("system")
        self.all_modules.insert(0, self.all_modules.pop(system_index))
