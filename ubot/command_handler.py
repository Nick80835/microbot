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
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))

    async def handle_incoming(self, event):
        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for key, value in self.incoming_commands.items():
            pattern = self.pattern_template.format("" if value["noprefix"] else prefix, key)

            if search(pattern, event.text):
                event.pattern_match = search(pattern, event.text)

                if value["sudo"] and str(event.from_id) != self.settings.get_config("owner_id"):
                    print(f"Attempted sudo command ({event.text}) from ID {event.from_id}")
                    return

                try:
                    await value["function"](event)
                    return
                except Exception as exception:
                    self.logger.warn(f"{value['function'].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception

                break
