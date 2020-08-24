# SPDX-License-Identifier: GPL-2.0-or-later

from time import time_ns

from ubot.micro_bot import ldr


@ldr.add("del", help="Deletes messages from this bot, it's a safety feature.")
async def delete_message(event):
    message_to_delete = await event.get_reply_message()

    if message_to_delete and message_to_delete.from_id == (await event.client.get_me()).id:
        await message_to_delete.delete()


@ldr.add("help")
async def help_cmd(event):
    if event.args:
        for key, value in ldr.help_dict.items():
            for info in value:
                if event.args == info[0]:
                    if info[1]:
                        await event.reply(f"Help for **{info[0]}**: __{info[1]}__")
                        return

                    await event.reply(f"**{info[0]}** doesn't have a help string.")
                    return

    prefix = ldr.prefix()
    help_string = ""

    for key, value in ldr.help_dict.items():
        help_string += f"\n**{key}**: "
        for info in value:
            help_string += f"{prefix}{info[0]}, "
        help_string = help_string.rstrip(", ")

    await event.reply(f"**Available commands:**\n{help_string}")


@ldr.add("sudohelp", sudo=True)
async def sudohelp(event):
    if event.args:
        for key, value in ldr.help_hidden_dict.items():
            for info in value:
                if event.args == info[0]:
                    if info[1]:
                        await event.reply(f"Help for **{info[0]}**: __{info[1]}__")
                        return

                    await event.reply(f"**{info[0]}** doesn't have a help string.")
                    return

    help_string = ""

    for key, value in ldr.help_hidden_dict.items():
        help_string += f"\n**{key}**: "
        for info in value:
            help_string += f"`{info[0]}`, "
        help_string = help_string.rstrip(", ")

    await event.reply(f"**Available (hidden) commands:**\n{help_string}")


@ldr.add("ping", hide_help=True)
async def ping(event):
    start = time_ns()
    ping_msg = await event.reply("Ping…")
    time_taken_ms = int((time_ns() - start) / 1000000)
    await ping_msg.edit(f"Ping… Pong! -> **{time_taken_ms}**ms")


@ldr.add("repo")
async def bot_repo(event):
    await event.reply("https://github.com/Nick80835/microbot")


@ldr.add("disable", admin=True, help="Disables commands in the current chat, requires admin.")
async def disable_command(event):
    if event.args:
        for value in ldr.help_dict.values():
            for info in value:
                if event.args == info[0]:
                    if info[2]:
                        await event.reply(f"**{info[0]}** cannot be disabled!")
                        return

                    await event.reply(f"Disabling **{info[0]}** in chat **{event.chat.id}**!")
                    ldr.db.disable_command(event.chat.id, info[0])
                    return

        await event.reply(f"**{event.args}** is not a command!")
    else:
        await event.reply(f"Specify a command to disable!")


@ldr.add("enable", admin=True, help="Enables commands in the current chat, requires admin.")
async def enable_command(event):
    if event.args:
        for value in ldr.help_dict.values():
            for info in [i[0] for i in value]:
                if event.args == info:
                    await event.reply(f"Enabling **{info}** in chat **{event.chat.id}**!")
                    ldr.db.enable_command(event.chat.id, info)
                    return

        await event.reply(f"**{event.args}** is not a command!")
    else:
        await event.reply(f"Specify a command to enable!")


@ldr.add("showdisabled", admin=True, help="Shows disabled commands in the current chat.")
async def show_disabled(event):
    disabled_list = ldr.db.get_disabled_commands(event.chat.id)

    if disabled_list:
        disabled_commands = "\n".join(ldr.db.get_disabled_commands(event.chat.id))
        await event.reply(f"Disabled commands in **{event.chat.id}**:\n\n{disabled_commands}")
    else:
        await event.reply(f"There are no disabled commands in **{event.chat.id}**!")


@ldr.add("nsfw", admin=True, help="Enables or disables NSFW commands for a chat, requires admin.")
async def nsfw_toggle(event):
    if not event.args or event.args not in ("on", "off"):
        if str(event.chat.id) not in ldr.settings.get_list("nsfw_blacklist"):
            current_config = 'On'
        else:
            current_config = 'Off'

        await event.reply(f"Syntax: {ldr.prefix()}nsfw (on|off)\nCurrent config for this chat: {current_config}")
        return

    if event.args == "on":
        ldr.settings.remove_from_list("nsfw_blacklist", event.chat.id)
        await event.reply("NSFW commands enabled for this chat!")
    elif event.args == "off":
        ldr.settings.add_to_list("nsfw_blacklist", event.chat.id)
        await event.reply("NSFW commands disabled for this chat!")


@ldr.add("fun", admin=True, help="Enables or disables fun commands for a chat, requires admin.")
async def fun_toggle(event):
    if not event.args or event.args not in ("on", "off"):
        if str(event.chat.id) not in ldr.settings.get_list("fun_blacklist"):
            current_config = 'On'
        else:
            current_config = 'Off'

        await event.reply(f"Syntax: {ldr.prefix()}fun (on|off)\nCurrent config for this chat: {current_config}")
        return

    if event.args == "on":
        ldr.settings.remove_from_list("fun_blacklist", event.chat.id)
        await event.reply("Fun commands enabled for this chat!")
    elif event.args == "off":
        ldr.settings.add_to_list("fun_blacklist", event.chat.id)
        await event.reply("Fun commands disabled for this chat!")
