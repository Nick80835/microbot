# SPDX-License-Identifier: GPL-2.0-or-later

import glob
from importlib import import_module, reload
from os.path import basename, dirname, isfile
from re import escape

from telethon import events
from telethon.tl.types import DocumentAttributeFilename

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
        self.command_handler.outgoing_commands = {}
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

    def add(self, pattern=None, **args):
        outgoing = args.get('outgoing', True)
        incoming = args.get('incoming', False)
        pattern = args.get("pattern", pattern)

        def decorator(func):
            if incoming:
                self.command_handler.incoming_commands[pattern] = {
                    "function": func,
                    "noprefix": args.get('noprefix', False),
                    "extras": args.get('extras', None)
                }
            elif outgoing:
                self.command_handler.outgoing_commands[pattern] = {
                    "function": func,
                    "noprefix": args.get('noprefix', False),
                    "extras": args.get('extras', None)
                }

            return func

        return decorator

    async def get_text(self, event, with_reply=True, return_msg=False, default=None):
        if event.args:
            if return_msg:
                if event.is_reply:
                    return event.args, await event.get_reply_message()

                return event.args, None

            return event.args
        elif event.is_reply and with_reply:
            reply = await event.get_reply_message()

            if return_msg:
                return reply.text, reply

            return reply.text
        else:
            if return_msg:
                return default, None

            return default

    async def get_image(self, event):
        if event and event.media:
            if event.photo:
                data = event.photo
            elif event.document:
                if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in event.media.document.attributes:
                    return False
                if event.gif or event.video or event.audio or event.voice:
                    return False
                data = event.media.document
            else:
                return False
        else:
            return False

        if not data or data is None:
            return False
        else:
            return data

    def _find_all_modules(self):
        mod_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = [
            basename(f)[:-3] for f in mod_paths
            if isfile(f) and f.endswith(".py")
        ]

        system_index = self.all_modules.index("system")
        self.all_modules.insert(0, self.all_modules.pop(system_index))
