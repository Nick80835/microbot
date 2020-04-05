# SPDX-License-Identifier: GPL-2.0-or-later

from re import escape, search

from telethon import events


class CommandHandler():
    def __init__(self, client, logger, settings):
        self.pattern_template = "(?is)^{0}{1}(?: |$)(.*)"
        self.outgoing_commands = {}
        self.incoming_commands = {}
        self.logger = logger
        self.settings = settings
        client.add_event_handler(self.handle_outgoing, events.NewMessage(outgoing=True))
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))

    async def handle_outgoing(self, event):
        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for key, value in self.outgoing_commands.items():
            pattern = self.pattern_template.format("" if value[1] else prefix, key)

            if search(pattern, event.text) and not event.via_bot_id:
                event.pattern_match = search(pattern, event.text)

                try:
                    await value[0](event)
                    return
                except Exception as exception:
                    self.logger.warn(f"{value[0].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value[0].__name__}: {exception}`")
                    raise exception

    async def handle_incoming(self, event):
        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for key, value in self.incoming_commands.items():
            pattern = self.pattern_template.format("" if value[1] else prefix, key)

            if search(pattern, event.text) and not event.via_bot_id:
                event.pattern_match = search(pattern, event.text)

                try:
                    await value[0](event)
                    return
                except Exception as exception:
                    self.logger.warn(f"{value[0].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value[0].__name__}: {exception}`")
                    raise exception
