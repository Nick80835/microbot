# SPDX-License-Identifier: GPL-2.0-or-later

import asyncio
from platform import python_version, uname
from time import time_ns

from telethon import version

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add("reload", sudo=True)
async def reload_modules(event):
    reload_msg = await event.reply("`Reloading modules…`")

    errors = ldr.reload_all_modules()

    if errors:
        await reload_msg.edit(errors)
    else:
        try:
            await reload_msg.edit("`Successfully reloaded.`")
        except:
            pass


@ldr.add("del")
async def delete_message(event):
    message_to_delete = await event.get_reply_message()
    if message_to_delete.from_id == (await event.client.get_me()).id:
        await message_to_delete.delete()


@ldr.add("help")
async def help_cmd(event):
    help_string = ""

    for key, value in ldr.help_dict.items():
        help_string += f"\n**{key}**: "
        for info in value:
            help_string += f"`{info}`, "
        help_string = help_string.rstrip(", ")

    await event.reply(f"`Available commands:`\n{help_string}")


@ldr.add("sysd", sudo=True)
async def sysd(event):
    try:
        neo = "neofetch --stdout"

        fetch = await asyncio.create_subprocess_shell(
            neo,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await fetch.communicate()

        await event.reply(f"`{stdout.decode().strip()}{stderr.decode().strip()}`")
    except FileNotFoundError:
        await event.reply("`Neofetch not found!`")


@ldr.add("alive", sudo=True)
async def alive(event):
    alive_format = "`μBot is running under {0}.\n\n" \
                   "Version: {1}\n" \
                   "Telethon: {2}\n" \
                   "Python: {3}`"

    await event.reply(alive_format.format(uname().node, ldr.botversion, version.__version__, python_version()))


@ldr.add("shutdown", sudo=True)
async def shutdown(event):
    await event.reply("`Goodbye…`")
    await micro_bot.stop_client()


@ldr.add("ping")
async def ping(event):
    start = time_ns()
    ping_msg = await event.reply("`Ping…`")
    time_taken_ms = int((time_ns() - start) / 1000000)
    await ping_msg.edit(f"`Ping… Pong! -> `**{time_taken_ms}**`ms`")


@ldr.add("repo")
async def bot_repo(event):
    await event.reply("https://github.com/Nick80835/microbot")
