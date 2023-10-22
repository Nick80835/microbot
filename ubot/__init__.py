import asyncio
import sys
from logging import INFO, basicConfig, getLogger
from time import time

import telethon
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import (AccessTokenExpiredError,
                                          AccessTokenInvalidError,
                                          TokenInvalidError)
from telethon.network.connection.tcpabridged import \
    ConnectionTcpAbridged as CTA

from .custom import (ExtendedCallbackQuery, ExtendedInlineQuery,
                     ExtendedNewMessage)
from .loader import Loader
from .settings import Settings

if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 10):
    print("This program requires at least Python 3.10.0 to work correctly, exiting.")
    sys.exit(1)

basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO)
logger = getLogger(__name__)
startup_time = time()
loop = asyncio.get_event_loop()

client: TelegramClient
ldr: Loader


class MicroBot():
    settings = Settings()
    logger = logger
    client: TelegramClient
    loader: Loader

    def __init__(self):
        loop.run_until_complete(self._initialize_bot())

    async def _initialize_bot(self):
        global client
        global ldr

        try:
            self.client = await TelegramClient(
                self.settings.get_config("session_name", "bot0") or "bot0",
                self.settings.get_config("api_id"),
                self.settings.get_config("api_hash"),
                connection=CTA
            ).start(
                bot_token=self.settings.get_config("bot_token")
            )
        except (TokenInvalidError, AccessTokenExpiredError, AccessTokenInvalidError):
            logger.error("The bot token provided is invalid, exiting.")
            sys.exit(1)

        self.me = await self.client.get_me()
        self.loader = Loader(self)
        client = self.client
        ldr = self.loader
        self.loader.load_all_modules()
        logger.info("Bot successfully started.")

    async def run_until_done(self):
        await self.client.run_until_disconnected()
        await self.stop_client(reason="Bot disconnected.")

    async def stop_client(self, reason=None, exit_code=None):
        if reason:
            logger.info("Stopping bot for reason: %s", reason)
        else:
            logger.info("Stopping bot.")

        await self.loader.aioclient.close()

        if exit_code is not None:
            logger.info("Exiting with exit code: %i", exit_code)
            sys.exit(exit_code)
        else:
            sys.exit(0)


telethon.events.NewMessage.Event = ExtendedNewMessage
telethon.events.CallbackQuery.Event = ExtendedCallbackQuery
telethon.events.InlineQuery.Event = ExtendedInlineQuery

micro_bot = MicroBot()

try:
    loop.run_until_complete(micro_bot.run_until_done())
except KeyboardInterrupt:
    loop.run_until_complete(micro_bot.stop_client())
