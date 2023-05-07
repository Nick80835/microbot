import sys
from logging import INFO, basicConfig, getLogger
from time import time

import telethon
from telethon.errors.rpcerrorlist import (AccessTokenExpiredError,
                                          AccessTokenInvalidError,
                                          TokenInvalidError)
from telethon.network.connection.tcpabridged import \
    ConnectionTcpAbridged as CTA

from .custom import ExtendedEvent
from .loader import Loader
from .settings import Settings

if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
    print("This program requires at least Python 3.6.0 to work correctly, exiting.")
    sys.exit(1)

startup_time = time()


class MicroBot():
    client = None
    settings = Settings()
    logger = None
    loader = None

    def __init__(self):
        basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO)
        self.logger = getLogger(__name__)
        self.start_client()
        self.loader = Loader(self.client, self.logger, self.settings)

    async def run_until_done(self):
        self.loader.load_all_modules()
        self.logger.info("Client successfully started.")
        await self.client.run_until_disconnected()
        await self.stop_client(reason="Client disconnected.")

    def _check_config(self):
        api_key = self.settings.get_config("api_key")
        api_hash = self.settings.get_config("api_hash")
        bot_token = self.settings.get_config("bot_token")

        while not api_key:
            api_key = input("Enter your API key: ")

        self.settings.set_config("api_key", api_key)

        while not api_hash:
            api_hash = input("Enter your API hash: ")

        self.settings.set_config("api_hash", api_hash)

        while not bot_token:
            bot_token = input("Enter your bot token: ")

        self.settings.set_config("bot_token", bot_token)

        return api_key, api_hash, bot_token

    def start_client(self):
        api_key, api_hash, bot_token = self._check_config()

        try:
            self.client = telethon.TelegramClient(self.settings.get_config("session_name", "bot0"), api_key, api_hash, connection=CTA).start(bot_token=bot_token)
        except (TokenInvalidError, AccessTokenExpiredError, AccessTokenInvalidError):
            self.logger.error("The bot token provided is invalid, exiting.")
            sys.exit(1)

    async def stop_client(self, reason=None, exit_code=None):
        if reason:
            self.logger.info("Stopping bot for reason: %s", reason)
        else:
            self.logger.info("Stopping bot.")

        await self.loader.aioclient.close()

        if exit_code is not None:
            self.logger.info("Exiting with exit code: %i", exit_code)
            sys.exit(exit_code)
        else:
            sys.exit(0)


telethon.events.NewMessage.Event = ExtendedEvent

micro_bot = MicroBot()
ldr = micro_bot.loader
client = micro_bot.client
logger = micro_bot.logger

client.loop.run_until_complete(micro_bot.run_until_done())
