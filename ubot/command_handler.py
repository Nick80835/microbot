# SPDX-License-Identifier: GPL-2.0-or-later

import asyncio
from re import escape, search

from telethon import events, types


class CommandHandler():
    def __init__(self, client, logger, settings):
        self.username = client.loop.run_until_complete(client.get_me()).username
        self.pattern_template = "(?is)^{0}{1}(?: |$|_|@{2}(?: |$|_))(.*)"
        self.inline_pattern_template = "(?is)^{0}(?: |$|_)(.*)"
        self.incoming_commands = {}
        self.inline_photo_commands = {}
        self.inline_article_commands = {}
        self.logger = logger
        self.settings = settings
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))
        client.add_event_handler(self.handle_inline, events.InlineQuery())

    async def handle_incoming(self, event):
        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for key, value in self.incoming_commands.items():
            pattern_match = search(self.pattern_template.format("" if value["noprefix"] else prefix, key, self.username), event.text)

            if pattern_match:
                if value["sudo"] and str(event.from_id) not in self.settings.get_list("owner_id"):
                    print(f"Attempted sudo command ({event.text}) from ID {event.from_id}")
                    continue
                elif value["admin"] and str(event.from_id) not in self.settings.get_list("owner_id") and not await self.check_admin(event):
                    print(f"Attempted admin command ({event.text}) from ID {event.from_id}")
                    continue

                if value["nsfw"] and str(event.chat.id) in self.settings.get_list("nsfw_blacklist"):
                    print(f"Attempted NSFW command ({event.text}) in blacklisted chat ({event.chat.id}) from ID {event.from_id}")
                    continue

                event.pattern_match = pattern_match
                event.args = pattern_match.groups()[-1]
                event.extras = value["extras"]

                try:
                    await value["function"](event)
                except Exception as exception:
                    self.logger.warn(f"{value['function'].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception

    async def handle_inline(self, event):
        for key, value in self.inline_photo_commands.items():
            pattern_match = search(self.inline_pattern_template.format(key), event.text)

            if pattern_match:
                await self.handle_inline_photo(event, pattern_match, value)
                return

        for key, value in self.inline_article_commands.items():
            pattern_match = search(self.inline_pattern_template.format(key), event.text)

            if pattern_match:
                await self.handle_inline_article(event, pattern_match, value)
                return

        await self.fallback_inline(event)

    async def handle_inline_photo(self, event, pattern_match, value):
        builder = event.builder
        event.pattern_match = pattern_match
        event.args = pattern_match.groups()[-1]

        url_list = await value["function"](event)

        if not url_list:
            return

        photo_coros = []

        for url in url_list:
            try:
                photo_coros += [self.try_coro(builder.photo(url))]
            except:
                pass

        if photo_coros:
            photos = await asyncio.gather(*photo_coros)
        else:
            return

        try:
            await event.answer([i for i in photos if i], gallery=True)
        except:
            pass

    async def handle_inline_article(self, event, pattern_match, value):
        builder = event.builder
        event.pattern_match = pattern_match
        event.args = pattern_match.groups()[-1]

        result_list = await value["function"](event)

        if not result_list:
            return

        articles = []

        for result in result_list:
            try:
                articles += [await builder.article(title=result["title"], description=result["description"], text=result["text"])]
            except:
                pass

        try:
            await event.answer([i for i in articles if i])
        except:
            pass

    async def fallback_inline(self, event):
        defaults_dict = {**self.inline_photo_commands, **self.inline_article_commands}

        try:
            await event.answer([await event.builder.article(title=key, text=f"{self.settings.get_config('cmd_prefix') or '.'}{value['default']}") for key, value in defaults_dict.items() if value["default"]])
        except:
            pass

    async def try_coro(self, coro):
        try:
            return await coro
        except:
            return

    async def check_admin(self, event):
        async for user in event.client.iter_participants(event.chat, limit=10000, filter=types.ChannelParticipantsAdmins):
            if user.id == event.from_id:
                return True

        return False
