# SPDX-License-Identifier: GPL-2.0-or-later

from platform import python_version, uname
from time import time_ns

from telethon import version

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="reload", sudo=True)
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


@ldr.add(pattern="alive", sudo=True)
async def alive(event):
    alive_format = "`μBot is running under {0}.\n\n" \
                   "Version: {1}\n" \
                   "Telethon: {2}\n" \
                   "Python: {3}`"

    await event.reply(alive_format.format(uname().node, ldr.botversion, version.__version__, python_version()))


@ldr.add(pattern="shutdown", sudo=True)
async def shutdown(event):
    await event.reply("`Goodbye…`")
    await micro_bot.stop_client()


@ldr.add(pattern="repo")
async def bot_repo(event):
    await event.reply("https://github.com/Nick80835/microbot")
