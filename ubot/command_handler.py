# SPDX-License-Identifier: GPL-2.0-or-later

import asyncio
from re import escape, search

from telethon import events, types

from .fixes import inline_photos


class CommandHandler():
    def __init__(self, client, logger, settings):
        self.username = client.loop.run_until_complete(client.get_me()).username
        self.pattern_template = "(?is)^{0}{1}(?: |$|_|@{2}(?: |$|_))(.*)"
        self.inline_pattern_template = "(?is)^{0}(?: |$|_)(.*)"
        self.incoming_commands = []
        self.inline_photo_commands = []
        self.inline_article_commands = []
        self.callback_queries = []
        self.logger = logger
        self.settings = settings
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))
        client.add_event_handler(self.handle_inline, events.InlineQuery())
        client.add_event_handler(self.handle_callback_query, events.CallbackQuery())

    async def handle_incoming(self, event):
        prefix = escape(self.settings.get_config("cmd_prefix") or '.')

        for value in self.incoming_commands:
            pattern_match = search(self.pattern_template.format("" if value["noprefix"] else prefix, value["pattern"], self.username), event.text)

            if pattern_match:
                if self.is_blacklisted(event):
                    print(f"Attempted command ({event.text}) from blacklisted ID {event.from_id}")
                    return

                if value["owner"] and not self.is_owner(event):
                    print(f"Attempted owner command ({event.text}) from ID {event.from_id}")
                    continue
                elif value["sudo"] and not self.is_sudo(event) and not self.is_owner(event):
                    print(f"Attempted sudo command ({event.text}) from ID {event.from_id}")
                    continue
                elif value["admin"] and not await self.is_admin(event) and not self.is_sudo(event) and not self.is_owner(event):
                    print(f"Attempted admin command ({event.text}) from ID {event.from_id}")
                    continue

                if value["nsfw"] and str(event.chat.id) in self.settings.get_list("nsfw_blacklist"):
                    print(f"Attempted NSFW command ({event.text}) in blacklisted chat ({event.chat.id}) from ID {event.from_id}")
                    continue

                event.pattern_match = pattern_match
                event.args = pattern_match.groups()[-1]
                event.extras = value["extras"]

                try:
                    if value["locking"]:
                        if value["lockreason"]:
                            await event.reply(f"That command is currently locked: {value['lockreason']}")
                            continue
                        else:
                            value["lockreason"] = f"In use by **{event.from_id}** (`{event.text}`)"
                            await value["function"](event)
                            value["lockreason"] = None
                    elif value["userlocking"]:
                        if event.from_id in value["lockedusers"]:
                            await event.reply(f"Please don't spam that command.")
                            continue
                        else:
                            value["lockedusers"].append(event.from_id)
                            await value["function"](event)
                            value["lockedusers"].remove(event.from_id)
                    else:
                        await value["function"](event)
                except Exception as exception:
                    value["lockreason"] = None

                    if event.from_id in value["lockedusers"]:
                        value["lockedusers"].remove(event.from_id)

                    self.logger.warn(f"{value['function'].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception

    async def handle_inline(self, event):
        for value in self.inline_photo_commands:
            pattern_match = search(self.inline_pattern_template.format(value["pattern"]), event.text)

            if pattern_match:
                if self.is_blacklisted(event, True):
                    print(f"Attempted command ({event.text}) from blacklisted ID {event.from_id}")
                    return

                await self.handle_inline_photo(event, pattern_match, value)
                return

        for value in self.inline_article_commands:
            pattern_match = search(self.inline_pattern_template.format(value["pattern"]), event.text)

            if pattern_match:
                if self.is_blacklisted(event, True):
                    print(f"Attempted command ({event.text}) from blacklisted ID {event.from_id}")
                    return

                await self.handle_inline_article(event, pattern_match, value)
                return

        await self.fallback_inline(event)

    async def handle_inline_photo(self, event, pattern_match, value):
        builder = event.builder
        event.pattern_match = pattern_match
        event.args = pattern_match.groups()[-1]

        photo_list = await value["function"](event)

        if not photo_list:
            return

        photo_coros = []

        for photo in photo_list:
            try:
                if isinstance(photo, list):
                    photo_coros += [self.try_coro(inline_photos.photo(event.client, photo[0], text=photo[1]))]
                else:
                    photo_coros += [self.try_coro(builder.photo(photo))]
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

    async def handle_callback_query(self, event):
        data_str = event.data.decode("utf-8")
        data_id = data_str.split("*")[0]
        data_data = data_str.lstrip(data_id + "*")

        for value in self.callback_queries:
            if value["data_id"] == data_id:
                event.args = data_data
                event.extras = value["extras"]

                try:
                    await value["function"](event)
                except Exception as exception:
                    self.logger.warn(f"{value['function'].__name__} - {exception}")
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception

    async def fallback_inline(self, event):
        defaults_list = self.inline_photo_commands + self.inline_article_commands

        try:
            await event.answer([await event.builder.article(title=value["pattern"], text=f"{self.settings.get_config('cmd_prefix') or '.'}{value['default']}") for value in defaults_list if value["default"]])
        except:
            pass

    async def try_coro(self, coro):
        try:
            return await coro
        except:
            return

    def is_owner(self, event):
        if str(event.from_id) in self.settings.get_list("owner_id"):
            return True
        else:
            return False

    def is_sudo(self, event):
        if str(event.from_id) in self.settings.get_list("sudo_users"):
            return True
        else:
            return False

    async def is_admin(self, event):
        async for user in event.client.iter_participants(event.chat, limit=10000, filter=types.ChannelParticipantsAdmins):
            if user.id == event.from_id:
                return True

        return False

    def is_blacklisted(self, event, inline=False):
        if inline:
            user_id = event.query.user_id
        else:
            user_id = event.from_id

        if str(user_id) in self.settings.get_list("blacklisted_users"):
            return True
        else:
            return False
