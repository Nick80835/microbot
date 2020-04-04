# SPDX-License-Identifier: GPL-2.0-or-later

from re import escape, search

from telethon import events


class CommandHandler():
    def __init__(self, client, logger, settings):
        self.outgoing_commands = {}
        self.incoming_commands = {}
        self.logger = logger
        self.settings = settings
        client.add_event_handler(self.handle_outgoing, events.NewMessage(outgoing=True))
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))

    async def handle_outgoing(self, event):
        for cmd in self.outgoing_commands.keys():
            if search(cmd, event.text) and not event.via_bot_id:
                event.pattern_match = search(cmd, event.text)

                try:
                    await self.outgoing_commands.get(cmd)(event)
                    return
                except Exception as exception:
                    self.logger.warn(f"{self.outgoing_commands.get(cmd).__name__} - {exception}")
                    await event.reply(f"`An error occurred in {self.outgoing_commands.get(cmd).__name__}: {exception}`")
                    raise exception

    async def handle_incoming(self, event):
        if not self.settings.get_bool("incoming_allowed"):
            return

        for cmd in self.incoming_commands.keys():
            if search(cmd, event.text) and not event.via_bot_id:
                event.pattern_match = search(cmd, event.text)

                try:
                    await self.incoming_commands.get(cmd)(event)
                    return
                except Exception as exception:
                    self.logger.warn(f"{self.incoming_commands.get(cmd).__name__} - {exception}")
                    await event.reply(f"`An error occurred in {self.incoming_commands.get(cmd).__name__}: {exception}`")
                    raise exception
