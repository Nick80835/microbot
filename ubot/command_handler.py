import asyncio
from random import randint
from re import escape, search
from traceback import format_exc, print_exc

from telethon import events

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
        client.add_event_handler(self.report_incoming_excepts, events.NewMessage(incoming=True, func=lambda e: e.raw_text and not e.fwd_from))
        client.add_event_handler(self.handle_inline, events.InlineQuery())
        client.add_event_handler(self.handle_callback_query, events.CallbackQuery())

    async def report_incoming_excepts(self, event):
        try:
            await self.handle_incoming(event)
        except:
            await event.client.send_message(int(self.settings.get_list("owner_id")[0]), str(format_exc()))

    async def handle_incoming(self, event):
        prefix = "|".join([escape(i) for i in (self.settings.get_list("cmd_prefix") or ['.'])])

        for command in self.incoming_commands:
            if command.simple_pattern:
                pattern_match = search(self.inline_pattern_template.format(command.pattern + command.pattern_extra), event.raw_text)
            elif command.raw_pattern:
                pattern_match = search(self.raw_pattern_template.format(command.pattern + command.pattern_extra), event.raw_text)
            else:
                pattern_match = search(self.pattern_template.format(f"({prefix})", command.pattern + command.pattern_extra, self.username), event.raw_text)

            if pattern_match:
                if not await self.check_privs(event, command):
                    return

                if command.pass_nsfw:
                    event.nsfw_disabled = str(event.chat.id) in self.settings.get_list("nsfw_blacklist")

                if command.raw_pattern:
                    event.command = command.pattern
                else:
                    event.command = pattern_match.groups()[1]

                if event.chat and not command.not_disableable and event.command in self.loader.db.get_disabled_commands(event.chat.id):
                    print(f"Attempted command ({event.raw_text}) in chat which disabled it ({event.chat.id}) from ID {event.sender_id}")
                    return

                if not command.raw_pattern:
                    event.args = pattern_match.groups()[-1].strip()

                    if command.simple_pattern:
                        event.other_args = pattern_match.groups()[1:-1]
                    else:
                        event.other_args = pattern_match.groups()[2:-1]

                event.pattern_match = pattern_match
                event.extra = command.extra
                event.object = command

                await self.execute_command(event, command)

    async def handle_inline(self, event):
        for command in self.inline_photo_commands:
            pattern_match = search(self.inline_pattern_template.format(command.pattern + command.pattern_extra), event.text)

            if pattern_match:
                if self.is_blacklisted(event, True) and not self.is_owner(event) and not self.is_sudo(event):
                    print(f"Attempted command ({event.text}) from blacklisted ID {event.sender_id}")
                    return

                await self.handle_inline_photo(event, pattern_match, command)
                return

        for command in self.inline_article_commands:
            pattern_match = search(self.inline_pattern_template.format(command.pattern + command.pattern_extra), event.text)

            if pattern_match:
                if self.is_blacklisted(event, True) and not self.is_owner(event) and not self.is_sudo(event):
                    print(f"Attempted command ({event.text}) from blacklisted ID {event.sender_id}")
                    return

                await self.handle_inline_article(event, pattern_match, command)
                return

        await self.fallback_inline(event)

    async def handle_inline_photo(self, event, pattern_match, command):
        builder = event.builder
        event.pattern_match = pattern_match
        event.args = pattern_match.groups()[-1]
        event.other_args = pattern_match.groups()[1:-1]
        event.command = pattern_match.groups()[0]
        event.extra = command.extra
        event.object = command
        event.parse_mode = command.parse_mode

        photo_list = await command.function(event)

        if not photo_list:
            return

        photo_coros = []

        for photo in photo_list:
            try:
                if isinstance(photo, list):
                    photo_coros += [
                        self.try_coro(inline_photos.photo(
                            event.client,
                            photo[0],
                            text=photo[1],
                            parse_mode=event.parse_mode
                        ))
                    ]
                else:
                    photo_coros += [self.try_coro(builder.photo(photo))]
            except:
                print_exc()

        if photo_coros:
            photos = await asyncio.gather(*photo_coros)
        else:
            return

        try:
            await event.answer([i for i in photos if i], gallery=True)
        except:
            print_exc()

    async def handle_inline_article(self, event, pattern_match, command):
        builder = event.builder
        event.pattern_match = pattern_match
        event.args = pattern_match.groups()[-1]
        event.other_args = pattern_match.groups()[1:-1]
        event.command = pattern_match.groups()[0]
        event.extra = command.extra
        event.object = command
        event.link_preview = command.link_preview
        event.parse_mode = command.parse_mode

        result_list = await command.function(event)

        if not result_list:
            return

        articles = []

        for result in result_list:
            try:
                articles += [
                    await builder.article(
                        title=result["title"],
                        description=result["description"],
                        text=result["text"],
                        link_preview=event.link_preview,
                        parse_mode=event.parse_mode
                    )
                ]
            except:
                print_exc()

        try:
            await event.answer([i for i in articles if i])
        except:
            print_exc()

    async def handle_callback_query(self, event):
        data_str = event.data.decode("utf-8")
        data_id = data_str.split("*")[0]
        data_data = data_str.lstrip(data_id + "*")

        for command in self.callback_queries:
            if command.data_id == data_id:
                event.command = data_id
                event.args = data_data
                event.extra = command.extra
                event.object = command

                try:
                    await command.function(event)
                except Exception as exception:
                    await event.reply(f"An error occurred in **{command.function.__name__}**: `{exception}`")
                    print_exc()

    async def fallback_inline(self, event):
        defaults_list = self.inline_photo_commands + self.inline_article_commands

        try:
            await event.answer([await event.builder.article(title=command.pattern, text=f"{self.loader.prefix()}{command.default}") for command in defaults_list if command.default])
        except:
            print_exc()

    async def try_coro(self, coro):
        try:
            return await coro
        except:
            return

    async def execute_command(self, event, command):
        try:
            if command.locking:
                if command.lock_reason:
                    await event.reply(f"That command is currently locked: {command.lock_reason}")
                    return

                if command.chance and randint(0, 100) <= command.chance or not command.chance:
                    command.lock_reason = f"In use by **{event.sender_id}** (`{event.raw_text}`)"
                    await command.function(event)
                    command.lock_reason = None
            elif command.user_locking:
                if event.sender_id in command.locked_users:
                    await event.reply(f"Please don't spam that command.")
                    return

                if command.chance and randint(0, 100) <= command.chance or not command.chance:
                    command.locked_users.append(event.sender_id)
                    await command.function(event)
                    command.locked_users.remove(event.sender_id)
            else:
                if command.chance and randint(0, 100) <= command.chance or not command.chance:
                    await command.function(event)
        except Exception as exception:
            command.lock_reason = None

            if event.sender_id in command.locked_users:
                command.locked_users.remove(event.sender_id)

            try:
                await event.reply(f"An error occurred in **{command.function.__name__}**: `{exception}`")
            except:
                pass

            print_exc()

    async def check_privs(self, event, command):
        if self.is_blacklisted(event) and not self.is_owner(event) and not self.is_sudo(event):
            print(f"Attempted command ({event.raw_text}) from blacklisted ID {event.sender_id}")
            return False

        if command.owner and not self.is_owner(event):
            await event.reply("You lack the permissions to use that command!")
            print(f"Attempted owner command ({event.raw_text}) from ID {event.sender_id}")
            return False

        if command.sudo and not self.is_sudo(event) and not self.is_owner(event):
            await event.reply("You lack the permissions to use that command!")
            print(f"Attempted sudo command ({event.raw_text}) from ID {event.sender_id}")
            return False

        if command.admin:
            if event.chat and event.sender_id:
                if event.is_private or not (await event.client.get_permissions(event.chat, event.sender_id)).is_admin and not self.is_sudo(event) and not self.is_owner(event):
                    await event.reply("You lack the permissions to use that command!")
                    print(f"Attempted admin command ({event.raw_text}) from ID {event.sender_id}")
                    return False

        if event.chat and command.nsfw and str(event.chat.id) in self.settings.get_list("nsfw_blacklist"):
            await event.reply("NSFW commands are disabled in this chat!")
            print(f"Attempted NSFW command ({event.raw_text}) in blacklisted chat ({event.chat.id}) from ID {event.sender_id}")
            return False

        if event.chat and command.fun and str(event.chat.id) in self.settings.get_list("fun_blacklist"):
            print(f"Attempted fun command ({event.raw_text}) in blacklisted chat ({event.chat.id}) from ID {event.sender_id}")
            return False

        return True

    def is_owner(self, event):
        return bool(str(event.sender_id) in self.settings.get_list("owner_id"))

    def is_sudo(self, event):
        return bool(str(event.sender_id) in self.settings.get_list("sudo_users"))

    def is_blacklisted(self, event, inline=False):
        if inline:
            user_id = event.query.user_id
        else:
            user_id = event.sender_id

        return bool(str(user_id) in self.settings.get_list("blacklisted_users"))
