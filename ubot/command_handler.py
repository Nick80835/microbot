# SPDX-License-Identifier: GPL-2.0-or-later

from re import escape, search

from telethon import events


class CommandHandler():
    def __init__(self, client, logger, settings):
        self.username = client.loop.run_until_complete(client.get_me()).username
        self.pattern_template = "(?is)^{0}{1}(?: |$|_|@{2}(?: |$|_))(.*)"
        self.incoming_commands = {}
        self.logger = logger
        self.settings = settings
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))

    async def handle_incoming(self, event):
        if event.via_bot_id:
            return

        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for key, value in self.incoming_commands.items():
            pattern_match = search(self.pattern_template.format("" if value["noprefix"] else prefix, key, self.username), event.text)

            if pattern_match:
                if value["sudo"] and str(event.from_id) not in self.settings.get_config("owner_id").split(","):
                    print(f"Attempted sudo command ({event.text}) from ID {event.from_id}")
                    continue

                event.pattern_match = pattern_match
                event.args = pattern_match.groups()[-1]

                try:
                    await value["function"](event)
                except Exception as exception:
                    self.logger.warn(f"{value['function'].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception
