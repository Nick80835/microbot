# SPDX-License-Identifier: GPL-2.0-or-later

from logging import INFO, basicConfig, getLogger
from sys import version_info

import telethon as tt
from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from telethon.network.connection.tcpabridged import \
    ConnectionTcpAbridged as CTA

from .loader import Loader
from .settings import Settings

if version_info[0] < 3 or version_info[1] < 6:
    print("This program requires at least Python 3.6.0 to work correctly, exiting.")
    quit(1)


class MicroBot():
    def __init__(self):
        self.client = None
        self.settings = Settings()
        self.logger = None
        self.loader = None

    def start_microbot(self):
        self.start_logger()
        self.start_client()
        self.start_loader()
        self.loader.load_all_modules()
        self.client.run_until_disconnected()

    def start_loader(self):
        self.loader = Loader(self.client, self.logger, self.settings)

    def start_logger(self):
        basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO)
        self.logger = getLogger(__name__)

    def _check_config(self, api_key, api_hash, session_name):
        while api_key is None or api_key == "":
            api_key = input("Enter your API key: ")

        while api_hash is None or api_hash == "":
            api_hash = input("Enter your API hash: ")

        self.settings.set_config("api_key", api_key)
        self.settings.set_config("api_hash", api_hash)

        if session_name is None or session_name == "":
            session_name = "user0"
            self.settings.set_config("session_name", session_name)

        return api_key, api_hash, session_name

    def start_client(self):
        session_name = self.settings.get_config("session_name")
        api_key = self.settings.get_config("api_key")
        api_hash = self.settings.get_config("api_hash")

        api_key, api_hash, session_name = self._check_config(api_key, api_hash, session_name)

        self.client = tt.TelegramClient(session_name, api_key, api_hash, connection=CTA)

        try:
            self.client.start()
        except PhoneNumberInvalidError:
            self.logger.error("The phone number provided is invalid, exiting.")
            exit(2)

    async def stop_client(self, reason=None):
        if reason:
            self.logger.info("Stopping client for reason: %s", reason)
        else:
            self.logger.info("Stopping client.")

        await self.client.disconnect()


micro_bot = MicroBot()
micro_bot.start_microbot()
