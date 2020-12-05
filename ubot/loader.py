import glob
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from importlib import import_module, reload
from os.path import basename, dirname, isfile

from aiohttp import ClientSession
from telethon.tl.types import (DocumentAttributeFilename,
                               DocumentAttributeSticker)

from .command import Command
from .command_handler import CommandHandler


class Loader():
    aioclient = ClientSession()
    thread_pool = ThreadPoolExecutor()

    loaded_modules = []
    all_modules = []

    def __init__(self, client, logger, settings):
        self.client = client
        self.logger = logger
        self.settings = settings
        self.command_handler = CommandHandler(client, settings)

    def load_all_modules(self):
        self._find_all_modules()

        for module_name in self.all_modules:
            try:
                self.loaded_modules.append(import_module("ubot.modules." + module_name))
            except Exception as exception:
                self.logger.error(f"Error while loading {module_name}: {exception}")

    def reload_all_modules(self):
        self.command_handler.outgoing_commands = []

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
            self.command_handler.outgoing_commands.append(Command(func, args))

            return func

        return decorator

    def add_list(self, pattern: list = None, **args):
        pattern_list = args.get("pattern", pattern)

        def decorator(func):
            for pattern in pattern_list:
                this_args = args.copy()
                this_args["pattern"] = pattern
                self.command_handler.outgoing_commands.append(Command(func, this_args))

            return func

        return decorator

    def add_dict(self, pattern: dict = None, **args):
        pattern_dict = args.get("pattern", pattern)

        def decorator(func):
            for pattern, extra in pattern_dict.items():
                if isinstance(pattern, tuple):
                    for patt in pattern:
                        this_args = args.copy()
                        this_args["pattern"] = patt
                        this_args["extra"] = args.get('extra', extra)
                        self.command_handler.outgoing_commands.append(Command(func, this_args))
                else:
                    this_args = args.copy()
                    this_args["pattern"] = pattern
                    this_args["extra"] = args.get('extra', extra)
                    self.command_handler.outgoing_commands.append(Command(func, this_args))

            return func

        return decorator

    def get_cmds_by_func(self, func) -> list:
        return [i for i in self.command_handler.outgoing_commands if i.function == func]

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
                return reply.raw_text, reply

            return reply.raw_text
        else:
            if return_msg:
                return default, None

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

    async def is_sticker(self, event) -> bool:
        if event and event.sticker:
            attrs = [i.alt for i in event.sticker.attributes if isinstance(i, DocumentAttributeSticker)]

            if attrs and attrs[0]:
                return True

        return False

    async def run_async(self, function, *args):
        return await self.client.loop.run_in_executor(self.thread_pool, partial(function, *args))

    def prefix(self):
        return (self.settings.get_list('cmd_prefix') or ['.'])[0]

    def _find_all_modules(self):
        module_paths = glob.glob(dirname(__file__) + "/modules/*.py")

        self.all_modules = sorted([
            basename(f)[:-3] for f in module_paths
            if isfile(f) and f.endswith(".py")
        ])
