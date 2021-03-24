from time import time_ns

from telethon import Button
from ubot import ldr


@ldr.add("del", no_disable=True, help="Deletes messages from this bot, it's a safety feature.")
async def delete_message(event):
    message_to_delete = await event.get_reply_message()

    if message_to_delete and message_to_delete.sender_id == (await event.client.get_me()).id:
        await message_to_delete.delete()


@ldr.add("start", no_disable=True, help="A start command to start the bot so you know what this bot is capable of when you start it, dumbass.")
async def start_cmd(event):
    await event.reply(
        f"Hi I'm {ldr.settings.get_config('bot_name') or 'μBot'}, use /help to see what commands I have!",
        buttons=[Button.url("Creator", "https://t.me/Nick80835"), Button.url("Source", "https://github.com/Nick80835/microbot/tree/bot")],
        link_preview=False
    )


@ldr.add("help", no_disable=True)
async def help_cmd(event):
    if event.args:
        for command in ldr.command_handler.incoming_commands:
            if not command.hide_help:
                if event.args == command.pattern:
                    if command.help:
                        await event.reply(f"Help for **{command.pattern}**: __{command.help}__")
                        return

                    await event.reply(f"**{command.pattern}** doesn't have a help string.")
                    return

    help_dict = {}

    for command in ldr.command_handler.incoming_commands:
        if not command.hide_help:
            if command.module in help_dict:
                help_dict[command.module].append(event.prefix + command.pattern)
            else:
                help_dict[command.module] = [event.prefix + command.pattern]

    help_string = "\n".join([f"**{module}**: {', '.join(pattern_list)}" for module, pattern_list in help_dict.items()])

    await event.reply(f"**Available commands:**\n\n{help_string}")


@ldr.add("prefix", admin=True, no_private=True)
async def set_group_prefix(event):
    if not event.args:
        await event.reply(f"With this command you can set a custom prefix to replace `/`, the current prefix is `{ldr.db.get_prefix(event.chat.id)}` and this bot will always respond to `{ldr.prefix()}`")
        return

    if len(event.args) > 2:
        await event.reply("Custom prefixes must be 1 or 2 characters long!")
        return

    ldr.db.set_prefix(event.chat.id, event.args)
    await event.reply(f"Successfully set this groups prefix to `{event.args}`!")


@ldr.add("sudohelp", sudo=True)
async def sudohelp(event):
    if event.args:
        for command in ldr.command_handler.incoming_commands:
            if command.hide_help:
                if event.args == command.pattern:
                    if command.help:
                        await event.reply(f"Help for **{command.pattern}**: __{command.help}__")
                        return

                    await event.reply(f"**{command.pattern}** doesn't have a help string.")
                    return

    prefix = ldr.prefix()
    help_dict = {}

    for command in ldr.command_handler.incoming_commands:
        if command.hide_help:
            if command.module in help_dict:
                help_dict[command.module].append(prefix + command.pattern)
            else:
                help_dict[command.module] = [prefix + command.pattern]

    help_string = "\n".join([f"**{module}**: {', '.join(pattern_list)}" for module, pattern_list in help_dict.items()])

    await event.reply(f"**Available hidden commands:**\n\n{help_string}")


@ldr.add("ping", hide_help=True)
async def ping(event):
    start = time_ns()
    ping_msg = await event.reply("Ping…")
    time_taken_ms = int((time_ns() - start) / 1000000)
    await ping_msg.edit(f"Ping… Pong! -> **{time_taken_ms}**ms")


@ldr.add("repo")
async def bot_repo(event):
    await event.reply("https://github.com/Nick80835/microbot/tree/bot")


@ldr.add("disable", admin=True, help="Disables commands in the current chat, requires admin.")
async def disable_command(event):
    if event.args:
        for command in ldr.command_handler.incoming_commands:
            if event.args == command.pattern:
                if command.not_disableable:
                    await event.reply(f"**{command.pattern}** cannot be disabled!")
                    return

                await event.reply(f"Disabling **{command.pattern}** in chat **{event.chat.id}**!")
                ldr.db.disable_command(event.chat.id, command.pattern)
                return

        await event.reply(f"**{event.args}** is not a command!")
    else:
        await event.reply("Specify a command to disable!")


@ldr.add("enable", admin=True, help="Enables commands in the current chat, requires admin.")
async def enable_command(event):
    if event.args:
        for command in ldr.command_handler.incoming_commands:
            if event.args == command.pattern:
                await event.reply(f"Enabling **{command.pattern}** in chat **{event.chat.id}**!")
                ldr.db.enable_command(event.chat.id, command.pattern)
                return

        await event.reply(f"**{event.args}** is not a command!")
    else:
        await event.reply("Specify a command to enable!")


@ldr.add("showdisabled", admin=True, help="Shows disabled commands in the current chat.")
async def show_disabled(event):
    disabled_list = ldr.db.disabled_commands(event.chat.id)

    if disabled_list:
        disabled_commands = "\n".join(disabled_list)
        await event.reply(f"Disabled commands in **{event.chat.id}**:\n\n{disabled_commands}")
    else:
        await event.reply(f"There are no disabled commands in **{event.chat.id}**!")


@ldr.add("nsfw", admin=True, help="Enables or disables NSFW commands for a chat, requires admin.")
async def nsfw_toggle(event):
    if event.args.lower() not in ("on", "off"):
        if ldr.db.nsfw_enabled(event.chat.id):
            current_config = 'On'
        else:
            current_config = 'Off'

        await event.reply(f"Syntax: {ldr.prefix()}nsfw (on|off)\nCurrent config for this chat: {current_config}")
        return

    if event.args == "on":
        ldr.db.set_nsfw(event.chat.id, True)
        await event.reply("NSFW commands enabled for this chat!")
    elif event.args == "off":
        ldr.db.set_nsfw(event.chat.id, False)
        await event.reply("NSFW commands disabled for this chat!")


@ldr.add("fun", admin=True, help="Enables or disables fun commands for a chat, requires admin.")
async def fun_toggle(event):
    if event.args.lower() not in ("on", "off"):
        if ldr.db.fun_enabled(event.chat.id):
            current_config = 'On'
        else:
            current_config = 'Off'

        await event.reply(f"Syntax: {ldr.prefix()}fun (on|off)\nCurrent config for this chat: {current_config}")
        return

    if event.args.lower() == "on":
        ldr.db.set_fun(event.chat.id, True)
        await event.reply("Fun commands enabled for this chat!")
    elif event.args.lower() == "off":
        ldr.db.set_fun(event.chat.id, False)
        await event.reply("Fun commands disabled for this chat!")
