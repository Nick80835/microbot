# SPDX-License-Identifier: GPL-2.0-or-later

import asyncio
from random import randint
from re import escape, search

from telethon import events, functions, types

from .fixes import inline_photos


class CommandHandler():
    pattern_template = "(?is)^{0}({1})(?: |$|_|@{2}(?: |$|_))(.*)"
    inline_pattern_template = "(?is)^({0})(?: |$|_)(.*)"
    raw_pattern_template = "(?is){0}"

    incoming_commands = []
    inline_photo_commands = []
    inline_article_commands = []
    callback_queries = []

    def __init__(self, client, settings, loader):
        self.username = client.loop.run_until_complete(client.get_me()).username
        self.settings = settings
        self.loader = loader
        client.add_event_handler(self.handle_incoming, events.NewMessage(incoming=True))
        client.add_event_handler(self.handle_inline, events.InlineQuery())
        client.add_event_handler(self.handle_callback_query, events.CallbackQuery())

    async def handle_incoming(self, event):
        prefix = "|".join([escape(i) for i in (self.settings.get_list("cmd_prefix") or ['.'])])

        for value in self.incoming_commands:
            if value["simple_pattern"]:
                pattern_match = search(self.inline_pattern_template.format(value["pattern"] + value["pattern_extra"]), event.raw_text)
            elif value["raw_pattern"]:
                pattern_match = search(self.raw_pattern_template.format(value["pattern"] + value["pattern_extra"]), event.raw_text)
            else:
                pattern_match = search(self.pattern_template.format(f"({prefix})", value["pattern"] + value["pattern_extra"], self.username), event.raw_text)

            if pattern_match:
                if not await self.check_privs(event, value):
                    return

                if value["pass_nsfw"]:
                    event.nsfw_disabled = str(event.chat.id) in self.settings.get_list("nsfw_blacklist")

                event.command = pattern_match.groups()[1]

                if event.command in self.loader.db.get_disabled_commands(event.chat.id):
                    print(f"Attempted command ({event.raw_text}) in chat which disabled it ({event.chat.id}) from ID {event.from_id}")
                    return

                event.pattern_match = pattern_match
                event.args = pattern_match.groups()[-1].strip()
                event.other_args = pattern_match.groups()[2:-1]
                event.extra = value["extra"]

                await self.execute_command(event, value)

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
        event.other_args = pattern_match.groups()[1:-1]
        event.command = pattern_match.groups()[0]

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
        event.other_args = pattern_match.groups()[:-1]

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
                event.extra = value["extra"]

                try:
                    await value["function"](event)
                except Exception as exception:
                    await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
                    raise exception

    async def fallback_inline(self, event):
        defaults_list = self.inline_photo_commands + self.inline_article_commands

        try:
            await event.answer([await event.builder.article(title=value["pattern"], text=f"{self.loader.prefix()}{value['default']}") for value in defaults_list if value["default"]])
        except:
            pass

    async def try_coro(self, coro):
        try:
            return await coro
        except:
            return

    async def execute_command(self, event, value):
        try:
            if value["locking"]:
                if value["lockreason"]:
                    await event.reply(f"That command is currently locked: {value['lockreason']}")
                    return

                if value["chance"] and randint(0, 100) <= value["chance"] or not value["chance"]:
                    value["lockreason"] = f"In use by **{event.from_id}** (`{event.raw_text}`)"
                    await value["function"](event)
                    value["lockreason"] = None
            elif value["userlocking"]:
                if event.from_id in value["lockedusers"]:
                    await event.reply(f"Please don't spam that command.")
                    return

                if value["chance"] and randint(0, 100) <= value["chance"] or not value["chance"]:
                    value["lockedusers"].append(event.from_id)
                    await value["function"](event)
                    value["lockedusers"].remove(event.from_id)
            else:
                if value["chance"] and randint(0, 100) <= value["chance"] or not value["chance"]:
                    await value["function"](event)
        except Exception as exception:
            value["lockreason"] = None

            if event.from_id in value["lockedusers"]:
                value["lockedusers"].remove(event.from_id)

            await event.reply(f"`An error occurred in {value['function'].__name__}: {exception}`")
            raise exception

    async def check_privs(self, event, value):
        if self.is_blacklisted(event) and not self.is_owner(event) and not self.is_sudo(event):
            print(f"Attempted command ({event.raw_text}) from blacklisted ID {event.from_id}")
            return False

        if value["owner"] and not self.is_owner(event):
            print(f"Attempted owner command ({event.raw_text}) from ID {event.from_id}")
            return False

        if value["sudo"] and not self.is_sudo(event) and not self.is_owner(event):
            print(f"Attempted sudo command ({event.raw_text}) from ID {event.from_id}")
            return False

        if value["admin"] and not await self.is_admin(event) and not self.is_sudo(event) and not self.is_owner(event):
            print(f"Attempted admin command ({event.raw_text}) from ID {event.from_id}")
            return False

        if value["nsfw"] and str(event.chat.id) in self.settings.get_list("nsfw_blacklist"):
            print(f"Attempted NSFW command ({event.raw_text}) in blacklisted chat ({event.chat.id}) from ID {event.from_id}")
            return False

        if value["fun"] and str(event.chat.id) in self.settings.get_list("fun_blacklist"):
            print(f"Attempted fun command ({event.raw_text}) in blacklisted chat ({event.chat.id}) from ID {event.from_id}")
            return False

        return True

    def is_owner(self, event):
        return bool(str(event.from_id) in self.settings.get_list("owner_id"))

    def is_sudo(self, event):
        return bool(str(event.from_id) in self.settings.get_list("sudo_users"))

    async def is_admin(self, event):
        if event.is_private:
            return True

        channel_participant = await event.client(functions.channels.GetParticipantRequest(event.chat, event.from_id))
        return bool(isinstance(channel_participant.participant, (types.ChannelParticipantAdmin, types.ChannelParticipantCreator)))

    def is_blacklisted(self, event, inline=False):
        if inline:
            user_id = event.query.user_id
        else:
            user_id = event.from_id

        return bool(str(user_id) in self.settings.get_list("blacklisted_users"))
