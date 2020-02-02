# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from re import escape, search

from telethon import events


class CommandHandler():
    def __init__(self, client, logger):
        self.outgoing_commands = {}
        self.incoming_commands = {}
        self.logger = logger
        client.add_event_handler(self.handle_outgoing, events.NewMessage(outgoing=True))
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))

    async def handle_outgoing(self, event):
        for cmd in self.outgoing_commands.keys():
            if search(cmd, event.text):
                event.pattern_match = search(cmd, event.text)

                try:
                    await self.outgoing_commands.get(cmd)(event)
                    return
                except Exception as exception:
                    self.logger.warn(f"{self.outgoing_commands.get(cmd).__name__} - {exception}")
                    await event.reply(f"`An error occurred in {self.outgoing_commands.get(cmd).__name__}: {exception}`")

    async def handle_incoming(self, event):
        for cmd in self.incoming_commands.keys():
            if search(cmd, event.text):
                event.pattern_match = search(cmd, event.text)

                try:
                    await self.incoming_commands.get(cmd)(event)
                    return
                except Exception as exception:
                    self.logger.warn(f"{self.incoming_commands.get(cmd).__name__} - {exception}")
                    await event.reply(f"`An error occurred in {self.incoming_commands.get(cmd).__name__}: {exception}`")
