# SPDX-License-Identifier: GPL-2.0-or-later

from re import escape, search

from telethon import events


class CommandHandler():
    def __init__(self, client, logger, settings):
        self.pattern_template = "(?is)^{0}{1}(?: |$)(.*)"
        self.outgoing_commands = []
        self.incoming_commands = []
        self.logger = logger
        self.settings = settings
        client.add_event_handler(self.handle_outgoing, events.NewMessage(outgoing=True))
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))

    async def handle_outgoing(self, event):
        if event.via_bot_id:
            return

        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for value in self.outgoing_commands:
            pattern_match = search(self.pattern_template.format("" if value["noprefix"] else prefix, value["pattern"]), event.text)

            if pattern_match:
                event.pattern_match = pattern_match
                event.args = pattern_match.groups()[-1]
                event.extras = value["extras"]

                try:
                    await value["function"](event)
                except Exception as exception:
                    self.logger.warn(f"{value['function'].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception

    async def handle_incoming(self, event):
        if event.via_bot_id:
            return

        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for value in self.incoming_commands:
            pattern_match = search(self.pattern_template.format("" if value["noprefix"] else prefix, value["pattern"]), event.text)

            if pattern_match:
                event.pattern_match = pattern_match
                event.args = pattern_match.groups()[-1]

                try:
                    await value["function"](event)
                except Exception as exception:
                    self.logger.warn(f"{value['function'].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception
