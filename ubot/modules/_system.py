# SPDX-License-Identifier: GPL-2.0-or-later

import asyncio
import os
from platform import python_version
from time import time_ns

import psutil
from telethon import version

from ubot import ldr, micro_bot


@ldr.add("reload")
async def reload_modules(event):
    await event.edit("`Reloading modules…`")

    errors = ldr.reload_all_modules()

    if errors:
        await event.edit(errors)
    else:
        try:
            await event.delete()
        except:
            pass


@ldr.add("help")
async def help_cmd(event):
    if event.args:
        for command in ldr.command_handler.outgoing_commands:
            if event.args == command.pattern:
                if command.help:
                    await event.edit(f"Help for **{command.pattern}**: __{command.help}__")
                    return

                await event.edit(f"**{command.pattern}** doesn't have a help string.")
                return

    help_dict = {}

    for command in ldr.command_handler.outgoing_commands:
        if command.module in help_dict:
            help_dict[command.module].append(command.pattern)
        else:
            help_dict[command.module] = [command.pattern]

    help_string = "\n".join([f"**{module}**: {', '.join(pattern_list)}" for module, pattern_list in help_dict.items()])

    await event.edit(f"**Available commands:**\n\n{help_string}")


@ldr.add("sysd")
async def sysd(event):
    try:
        neo = "neofetch --stdout"

        fetch = await asyncio.create_subprocess_shell(
            neo,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await fetch.communicate()

        await event.edit(f"`{stdout.decode().strip()}{stderr.decode().strip()}`")
    except FileNotFoundError:
        await event.edit("`Neofetch not found!`")


@ldr.add("alive")
async def alive(event):
    alive_format = "μBot is running!\n" \
                   "**Telethon version:** {0}\n" \
                   "**Python version:** {1}\n" \
                   "**Memory usage:** {2}MiB"

    mem_usage = int(psutil.Process(os.getpid()).memory_info().rss / 1048576)

    await event.edit(alive_format.format(version.__version__, python_version(), mem_usage))


@ldr.add("shutdown")
async def shutdown(event):
    await event.edit("`Goodbye…`")
    await micro_bot.stop_client()


@ldr.add("ping")
async def ping(event):
    start = time_ns()
    await event.edit("`Ping…`")
    time_taken_ms = int((time_ns() - start) / 1000000)
    await event.edit(f"`Ping… Pong! -> `**{time_taken_ms}**`ms`")


@ldr.add("prefix")
async def change_prefix(event):
    new_prefix = event.args

    if not new_prefix:
        await event.edit("`Please specify a valid command prefix!`")
        return

    micro_bot.settings.set_config("cmd_prefix", new_prefix)

    await event.edit(f"`Command prefix successfully changed to `**{new_prefix}**`!`")


@ldr.add("repo")
async def bot_repo(event):
    await event.edit("https://github.com/Nick80835/microbot")


@ldr.add("support")
async def support_link(event):
    await event.edit("[μBot Support](https://t.me/joinchat/Ed1JxFLq3DtQSbBnyNRI7A)")
