# SPDX-License-Identifier: GPL-2.0-or-later

import glob
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module, reload
from os.path import basename, dirname, isfile

from aiohttp import ClientSession
from telethon.tl.types import DocumentAttributeFilename

from .command_handler import CommandHandler


class Loader():
    def __init__(self, client, logger, settings):
        self.loaded_modules = []
        self.all_modules = []
        self.client = client
        self.logger = logger
        self.settings = settings
        self.command_handler = CommandHandler(client, logger, settings, self)
        self.help_dict = {}
        self.help_hidden_dict = {}
        self.aioclient = ClientSession()
        self.thread_pool = ThreadPoolExecutor()

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
        self.help_dict = {}
        self.help_hidden_dict = {}

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
        pattern = args.get("pattern", pattern)

        def decorator(func):
            if args.get("hide_help", False):
                if func.__module__.split(".")[-1] in self.help_hidden_dict:
                    self.help_hidden_dict[func.__module__.split(".")[-1]] += [pattern]
                else:
                    self.help_hidden_dict[func.__module__.split(".")[-1]] = [pattern]
            else:
                if func.__module__.split(".")[-1] in self.help_dict:
                    self.help_dict[func.__module__.split(".")[-1]] += [pattern]
                else:
                    self.help_dict[func.__module__.split(".")[-1]] = [pattern]

            self.command_handler.incoming_commands.append({
                "pattern": pattern,
                "function": func,
                "simple_pattern": args.get('simple_pattern', False),
                "raw_pattern": args.get('raw_pattern', False),
                "sudo": args.get('sudo', False),
                "extras": args.get('extras', None),
                "nsfw": args.get('nsfw', False),
                "pass_nsfw": args.get('pass_nsfw', False),
                "admin": args.get('admin', False),
                "owner": args.get('owner', False),
                "locking": args.get('locking', False),
                "lockreason": None,
                "userlocking": args.get('userlocking', False),
                "lockedusers": [],
                "chance": args.get('chance', None)
            })

            return func

        return decorator

    def add_list(self, pattern=None, **args):
        pattern_list = args.get("pattern", pattern)
        pattern_extra = args.get("pattern_extra", "")

        def decorator(func):
            for pattern in pattern_list:
                if args.get("hide_help", False):
                    if func.__module__.split(".")[-1] in self.help_hidden_dict:
                        self.help_hidden_dict[func.__module__.split(".")[-1]] += [pattern]
                    else:
                        self.help_hidden_dict[func.__module__.split(".")[-1]] = [pattern]
                else:
                    if func.__module__.split(".")[-1] in self.help_dict:
                        self.help_dict[func.__module__.split(".")[-1]] += [pattern]
                    else:
                        self.help_dict[func.__module__.split(".")[-1]] = [pattern]

                self.command_handler.incoming_commands.append({
                    "pattern": pattern + pattern_extra,
                    "function": func,
                    "simple_pattern": args.get('simple_pattern', False),
                    "raw_pattern": args.get('raw_pattern', False),
                    "sudo": args.get('sudo', False),
                    "extras": args.get('extras', pattern),
                    "nsfw": args.get('nsfw', False),
                    "pass_nsfw": args.get('pass_nsfw', False),
                    "admin": args.get('admin', False),
                    "owner": args.get('owner', False),
                    "locking": args.get('locking', False),
                    "lockreason": None,
                    "userlocking": args.get('userlocking', False),
                    "lockedusers": []
                })

            return func

        return decorator

    def add_inline_photo(self, pattern=None, **args):
        pattern = args.get("pattern", pattern)

        def decorator(func):
            self.command_handler.inline_photo_commands.append({
                "pattern": pattern,
                "function": func,
                "default": args.get("default", None)
            })

            return func

        return decorator

    def add_inline_article(self, pattern=None, **args):
        pattern = args.get("pattern", pattern)

        def decorator(func):
            self.command_handler.inline_article_commands.append({
                "pattern": pattern,
                "function": func,
                "default": args.get("default", None)
            })

            return func

        return decorator

    def add_callback_query(self, data_id=None, **args):
        data_id = args.get("data_id", data_id)

        def decorator(func):
            self.command_handler.callback_queries.append({
                "data_id": data_id,
                "function": func,
                "extras": args.get('extras', None)
            })

            return func

        return decorator

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
                    return None
                if event.gif or event.video or event.audio or event.voice:
                    return None

                return event.media.document
            else:
                return None
        else:
            return None

    def prefix(self):
        return (self.settings.get_list('cmd_prefix') or ['.'])[0]

    def _find_all_modules(self):
        module_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = sorted([
            basename(f)[:-3] for f in module_paths
            if isfile(f) and f.endswith(".py")
        ])
