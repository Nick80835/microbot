# SPDX-License-Identifier: GPL-2.0-or-later

import glob
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module, reload
from os.path import basename, dirname, isfile

from aiohttp import ClientSession

from telethon.tl.types import DocumentAttributeFilename

from .cache import Cache
from .command import (CallbackQueryCommand, Command, InlineArticleCommand,
                      InlinePhotoCommand)
from .command_handler import CommandHandler
from .database import Database


class Loader():
    aioclient = ClientSession()
    thread_pool = ThreadPoolExecutor()
    cache = Cache(aioclient)
    db = Database()

    loaded_modules = []
    all_modules = []

    def __init__(self, client, logger, settings):
        self.client = client
        self.logger = logger
        self.settings = settings
        self.command_handler = CommandHandler(client, settings, self)

    def load_all_modules(self):
        self._find_all_modules()

        for module_name in self.all_modules:
            try:
                self.loaded_modules.append(import_module("ubot.modules." + module_name))
            except Exception as exception:
                self.logger.error(f"Error while loading {module_name}: {exception}")

    def reload_all_modules(self):
        self.command_handler.incoming_commands = []
        self.command_handler.inline_photo_commands = []
        self.command_handler.inline_article_commands = []
        self.command_handler.callback_queries = []

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

    def add(self, pattern: str = None, **args):
        def decorator(func):
            args["pattern"] = args.get("pattern", pattern)
            self.command_handler.incoming_commands.append(Command(func, args))

            return func

        return decorator

    def add_list(self, pattern: list = None, **args):
        pattern_list = args.get("pattern", pattern)

        def decorator(func):
            for pattern in pattern_list:
                this_args = args.copy()
                this_args["pattern"] = pattern
                self.command_handler.incoming_commands.append(Command(func, this_args))

            return func

        return decorator

    def add_dict(self, pattern: dict = None, **args):
        pattern_dict = args.get("pattern", pattern)

        def decorator(func):
            for pattern, extra in pattern_dict.items():
                this_args = args.copy()
                this_args["pattern"] = pattern
                this_args["extra"] = args.get('extra', extra)
                self.command_handler.incoming_commands.append(Command(func, this_args))

            return func

        return decorator

    def add_inline_photo(self, pattern=None, **args):
        def decorator(func):
            args["pattern"] = args.get("pattern", pattern)
            self.command_handler.inline_photo_commands.append(InlinePhotoCommand(func, args))

            return func

        return decorator

    def add_inline_article(self, pattern=None, **args):
        def decorator(func):
            args["pattern"] = args.get("pattern", pattern)
            self.command_handler.inline_article_commands.append(InlineArticleCommand(func, args))

            return func

        return decorator

    def add_callback_query(self, data_id=None, **args):
        def decorator(func):
            args["data_id"] = args.get("data_id", data_id)
            self.command_handler.callback_queries.append(CallbackQueryCommand(func, args))

            return func

        return decorator

    def get_cmds_by_func(self, func) -> list:
        return [i for i in self.command_handler.incoming_commands if i.function == func]

    def get_cbs_by_func(self, func) -> list:
        return [i for i in self.command_handler.callback_queries if i.function == func]

    async def get_text(self, event, with_reply=True, return_msg=False, default=None):
        if event.args:
            if return_msg:
                if event.is_reply:
                    return event.args, await event.get_reply_message()

                return event.args, event

            return event.args
        elif event.is_reply and with_reply:
            reply = await event.get_reply_message()

            if return_msg:
                return reply.text, reply

            return reply.text
        else:
            if return_msg:
                return default, event

            return default

    async def get_image(self, event):
        if event and event.media:
            if event.photo:
                return event.photo
            elif event.document:
                if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in event.media.document.attributes:
                    return
                if event.gif or event.video or event.audio or event.voice:
                    return

                return event.media.document
            else:
                return
        else:
            return

    def prefix(self):
        return (self.settings.get_list('cmd_prefix') or ['.'])[0]

    def _find_all_modules(self):
        module_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = sorted([
            basename(f)[:-3] for f in module_paths
            if isfile(f) and f.endswith(".py")
        ])
