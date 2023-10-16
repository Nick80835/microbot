# SPDX-License-Identifier: GPL-2.0-or-later

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
        self.command_handler = CommandHandler(client, logger, settings)
        self.botversion = "0.1.3"

    def load_all_modules(self):
        self._find_all_modules()

        for module_name in self.all_modules:
            self.loaded_modules.append(import_module("ubot.modules." + module_name))

    def reload_all_modules(self):
        self.command_handler.incoming_commands = {}

        errors = ""

        for module in self.loaded_modules:
            try:
                reload(module)
            except ModuleNotFoundError:
                pass
            except Exception as exception:
                errors += f"`Error while reloading {module.__name__} -> {exception}\n\n`"
                raise exception

        return errors or None

    def add(self, **args):
        def decorator(func):
            self.command_handler.incoming_commands[args['pattern']] = {
                "function": func,
                "noprefix": args.get('noprefix', False),
                "sudo": args.get('sudo', False)
            }

            return func

        return decorator

    def _find_all_modules(self):
        mod_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = [
            basename(f)[:-3] for f in mod_paths
            if isfile(f) and f.endswith(".py")
        ]

        system_index = self.all_modules.index("system")
        self.all_modules.insert(0, self.all_modules.pop(system_index))
