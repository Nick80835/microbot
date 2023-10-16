import asyncio
import inspect
import io
import os
import sys
from datetime import timedelta
from platform import python_version
from time import time
from traceback import print_exc

import git
import psutil
from telethon import version

from ubot import ldr, startup_time
from ubot.fixes.utils import get_user


@ldr.add("eval", owner=True, hide_help=True)
async def evaluate(event):
    if not event.args:
        await event.reply("Give me code to run!")
        return

    eval_msg = await event.reply("Processing…")

    # helpful variables
    reply = await event.get_reply_message()
    client = event.client

    try:
        eval_ret = eval(event.args)
    except Exception as exception:
        print_exc()
        eval_ret = exception

    if inspect.isawaitable(eval_ret):
        isawait = " (awaited)"
        eval_ret = await eval_ret
    else:
        isawait = ""

    if len(f"**Evaluation:**\n{event.args}\n**Return{isawait}:**\n{eval_ret}") > 4096:
        text_io = io.BytesIO(str(eval_ret).encode("utf-8"))
        text_io.name = "return.txt"
        await eval_msg.edit("Output too large for a message, sending as a file…")
        await eval_msg.reply(file=text_io)
        return

    await eval_msg.edit(f"**Evaluation:**\n{event.args}\n**Return{isawait}:**\n{eval_ret}")


@ldr.add("exec", owner=True, hide_help=True)
async def execute(event):
    exec_msg = await event.reply("Processing…")
    reply = await event.get_reply_message()
    client = event.client

    if not event.args:
        await event.edit("Give me code to run!")
        return

    temp_locals = {}

    try:
        exec(
            f'async def __ex(event, reply, client): ' +
            ''.join(f'\n {l}' for l in event.args.split('\n')),
            globals(),
            temp_locals
        )

        eval_ret = await temp_locals['__ex'](event, reply, client)
    except Exception as exception:
        print_exc()
        eval_ret = exception

    if len(f"**Execution:**\n`{event.args}`\n**Return:**\n`{eval_ret}`") > 4096:
        text_io = io.BytesIO(str(eval_ret).encode("utf-8"))
        text_io.name = "return.txt"
        await exec_msg.edit("Output too large for a message, sending as a file…")
        await event.respond(file=text_io)
        return

    await exec_msg.edit(f"**Execution:**\n`{event.args}`\n**Return:**\n`{eval_ret}`")


@ldr.add("reload", sudo=True, hide_help=True)
async def reload_modules(event):
    reload_msg = await event.reply("Reloading modules…")

    errors = ldr.reload_all_modules()

    if errors:
        await reload_msg.edit(errors)
    else:
        try:
            await reload_msg.edit("Successfully reloaded.")
        except:
            pass


@ldr.add("update", owner=True, hide_help=True)
async def update_bot(event):
    update_msg = await event.reply("Pulling changes…")
    repo = git.Repo(os.getcwd())
    repo.remotes.origin.pull()
    await update_msg.edit("Changes pulled successfully!")


@ldr.add("sysd", sudo=True, hide_help=True)
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
        await event.reply("Neofetch not found!")


@ldr.add("alive", sudo=True, hide_help=True)
async def alive(event):
    alive_format = "**Telethon version:** {0}\n" \
                   "**Python version:** {1}\n" \
                   "**Memory usage:** {2} MiB\n" \
                   "**Uptime:** {3}"

    await event.reply(
        alive_format.format(
            version.__version__,
            python_version(),
            int(psutil.Process(os.getpid()).memory_info().rss / 1048576),
            timedelta(seconds=int(time() - startup_time))
        )
    )


@ldr.add("dbstat", owner=True, hide_help=True)
async def dbstat(event):
    dbstat_format = "**Size on disk:** {0} MiB\n" \
                    "**Chat count:** {1}\n" \
                    "**Cache memory usage:** {2} MiB\n" \
                    "**Cached chat count:** {3}"

    await event.reply(
        dbstat_format.format(
            round(os.stat("database.sqlite").st_size / 1048576, 2),
            ldr.db.chat_table.select().count(),
            round(sys.getsizeof(ldr.db.cached_chat_wrappers) / 1048576, 2),
            len(ldr.db.cached_chat_wrappers)
        )
    )


@ldr.add("shutdown", pattern_extra="(f|)", owner=True, hide_help=True)
async def shutdown(event):
    await event.reply("Goodbye…")

    if event.other_args[0]:
        await ldr.micro_bot.stop_client(reason="Shutdown command issued.", exit_code=1)
    else:
        await ldr.micro_bot.stop_client(reason="Shutdown command issued.")


@ldr.add("blacklist", sudo=True, hide_help=True)
async def add_blacklist(event):
    user_entity = await get_user(event)

    if not user_entity:
        return

    userid = user_entity.id
    userfullname = f"{user_entity.first_name} {user_entity.last_name or ''}".strip()

    ldr.db.blacklist_user(userid)
    await event.reply(f"Successfully blacklisted **{userfullname}** (`{userid}`)")


@ldr.add("unblacklist", sudo=True, hide_help=True)
async def rem_blacklist(event):
    user_entity = await get_user(event)

    if not user_entity:
        return

    userid = user_entity.id
    userfullname = f"{user_entity.first_name} {user_entity.last_name or ''}".strip()

    ldr.db.unblacklist_user(userid)
    await event.reply(f"Successfully unblacklisted **{userfullname}** (`{userid}`)")


@ldr.add("showblacklist", sudo=True, hide_help=True)
async def show_blacklist(event):
    blacklist_string = "\n".join([str(user_id) for user_id in ldr.db.blacklisted_users])

    await event.reply(f"**Blacklisted users:**\n\n{blacklist_string}")


@ldr.add("sudo", owner=True, hide_help=True)
async def add_sudo(event):
    user_entity = await get_user(event)

    if not user_entity:
        return

    userid = user_entity.id
    userfullname = f"{user_entity.first_name} {user_entity.last_name or ''}".strip()

    ldr.db.sudo_user(userid)
    await event.reply(f"Successfully sudo'd **{userfullname}** (`{userid}`)")


@ldr.add("unsudo", owner=True, hide_help=True)
async def rem_sudo(event):
    user_entity = await get_user(event)

    if not user_entity:
        return

    userid = user_entity.id
    userfullname = f"{user_entity.first_name} {user_entity.last_name or ''}".strip()

    ldr.db.unsudo_user(userid)
    await event.reply(f"Successfully unsudo'd **{userfullname}** (`{userid}`)")


@ldr.add("showsudo", sudo=True, hide_help=True)
async def show_sudo(event):
    sudo_string = "\n".join([str(user_id) for user_id in ldr.db.sudo_users])
    await event.reply(f"**Sudo users:**\n\n{sudo_string}")
