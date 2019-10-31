import glob
from importlib import import_module
from os.path import basename, dirname, isfile
from re import escape

from telethon import events


class Loader():
    def __init__(self, client, cmd_prefix):
        self.loaded_modules = []
        self.all_modules = []
        self.client = client
        self.cmd_prefix = cmd_prefix or '.'
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
            self.client.add_event_handler(func, events.NewMessage(**args))
            return func

        return decorator

    def _find_all_modules(self):
        mod_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = [
            basename(f)[:-3] for f in mod_paths
            if isfile(f) and f.endswith(".py")
        ]
