import asyncio
import inspect
import io
import os
from platform import python_version

import psutil
from telethon import version
from telethon.tl.types import Channel, Chat

from ubot import ldr, micro_bot


@ldr.add("eval", owner=True, hide_help=True)
async def evaluate(event):
    if not event.args:
        await event.reply("Give me code to run!")
        return

    eval_msg = await event.reply("Processing…")
    reply = await event.get_reply_message()

    try:
        eval_ret = eval(event.args)
    except Exception as exception:
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

    if not event.args:
        await event.edit("Give me code to run!")
        return

    temp_locals = {}

    try:
        exec(
            f'async def __ex(event, reply): ' +
            ''.join(f'\n {l}' for l in event.args.split('\n')),
            globals(),
            temp_locals
        )

        eval_ret = await temp_locals['__ex'](event, reply)
    except Exception as exception:
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
                   "**Memory usage:** {2}MiB"

    mem_usage = int(psutil.Process(os.getpid()).memory_info().rss / 1048576)

    await event.reply(alive_format.format(version.__version__, python_version(), mem_usage))


@ldr.add("shutdown", owner=True, hide_help=True)
async def shutdown(event):
    await event.reply("Goodbye…")
    await micro_bot.stop_client()


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
    blacklist_string = "\n".join([str(user_id) for user_id in ldr.db.get_blacklist_list()])

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
    sudo_string = "\n".join([str(user_id) for user_id in ldr.db.get_sudo_list()])
    await event.reply(f"**Sudo users:**\n\n{sudo_string}")


async def get_user(event):
    if event.args:
        try:
            event.args = int(event.args)
        except:
            pass

        try:
            user = await event.client.get_entity(event.args)

            if isinstance(user, (Chat, Channel)):
                raise TypeError

            return user
        except (ValueError, TypeError):
            await event.reply("The ID or username you provided was invalid!")
            return
    elif event.is_reply:
        reply = await event.get_reply_message()
        reply_id = reply.sender_id

        if reply_id:
            try:
                user = await event.client.get_entity(reply_id)

                if isinstance(user, (Chat, Channel)):
                    raise TypeError

                return user
            except (ValueError, TypeError):
                await event.reply("There was an error getting the user's ID!")
                return
        else:
            await event.reply("Sudoing failed!")
            return
    else:
        await event.reply("Give me a user ID, username or reply!")
        return
