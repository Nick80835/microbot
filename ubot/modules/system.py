# SPDX-License-Identifier: GPL-2.0-or-later

from time import time_ns

from telethon import version

from ubot.micro_bot import ldr


@ldr.add("del")
async def delete_message(event):
    message_to_delete = await event.get_reply_message()

    if message_to_delete and message_to_delete.from_id == (await event.client.get_me()).id:
        await message_to_delete.delete()


@ldr.add("help")
async def help_cmd(event):
    help_string = ""

    for key, value in ldr.help_dict.items():
        help_string += f"\n**{key}**: "
        for info in value:
            help_string += f"`{info}`, "
        help_string = help_string.rstrip(", ")

    await event.reply(f"**Available commands:**\n{help_string}")


@ldr.add("sudohelp", sudo=True)
async def sudohelp(event):
    help_string = ""

    for key, value in ldr.help_hidden_dict.items():
        help_string += f"\n**{key}**: "
        for info in value:
            help_string += f"`{info}`, "
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


@ldr.add("nsfw", admin=True)
async def nsfw_toggle(event):
    if not event.args or event.args not in ("on", "off"):
        if str(event.chat.id) not in ldr.settings.get_list("nsfw_blacklist"):
            current_config = 'On'
        else:
            current_config = 'Off'

        await event.reply(f"Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}nsfw (on|off)\nCurrent config for this chat: {current_config}")
        return

    if event.args == "on":
        ldr.settings.remove_from_list("nsfw_blacklist", event.chat.id)
        await event.reply("NSFW commands enabled for this chat!")
    elif event.args == "off":
        ldr.settings.add_to_list("nsfw_blacklist", event.chat.id)
        await event.reply("NSFW commands disabled for this chat!")
