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
