# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import inspect

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="b2d")
async def bintodec(event):
    binary = event.pattern_match.group(1)

    if not binary:
        await event.edit("`Give me a binary number!`")
        return

    try:
        decimal = int(binary, 2)
    except ValueError:
        await event.edit("`Give me a binary number!`")
        return

    await event.edit(f"**{binary}** `=` **{decimal}**")


@ldr.add(pattern="d2b")
async def dectobin(event):
    try:
        decimal = int(event.pattern_match.group(1))
    except ValueError:
        await event.edit("`Give me a decimal number!`")
        return

    if not decimal:
        await event.edit("`Give me a decimal number!`")
        return

    binary = bin(decimal).replace("0b","") 

    await event.edit(f"**{decimal}** `=` **{binary}**")


@ldr.add(pattern="eval")
async def evaluate(event):
    code = event.pattern_match.group(1)

    if not code:
        await event.edit("`Give me code to run!`")
        return

    try:
        eval_ret = eval(code)
    except Exception as exception:
        eval_ret = exception

    if inspect.isawaitable(eval_ret):
        isawait = " (awaited)"
        eval_ret = await eval_ret
    else:
        isawait = ""

    await event.edit(f"**Evaluation:**\n`{code}`\n**Return{isawait}:**\n`{eval_ret}`")


@ldr.add(pattern="chatid")
async def chatidgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.forward and reply.forward.channel_id:
            await event.edit(f"**Channel ID:**` {reply.forward.channel_id}`")
            return
        chat_id = reply.chat_id
    else:
        chat_id = event.chat_id

    await event.edit(f"**Chat ID:**` {chat_id}`")


@ldr.add(pattern="userid")
async def useridgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.from_id
    else:
        user_id = event.from_id

    await event.edit(f"**User ID:**` {user_id}`")


@ldr.add(pattern="profile")
async def userprofilegetter(event):
    user_arg = event.pattern_match.group(1)

    if user_arg:
        try:
            user_entity = await event.client.get_entity(user_arg)
        except (ValueError, TypeError):
            await event.edit("`The ID or username you provided was invalid!`")
            return
    elif event.is_reply:
        reply = await event.get_reply_message()
        reply_id = reply.from_id
        if reply_id:
            try:
                user_entity = await event.client.get_entity(reply_id)
            except (ValueError, TypeError):
                await event.edit("`There was an error getting the user!`")
                return
        else:
            await event.edit("`The user may have super sneaky privacy settings enabled!`")
            return
    else:
        await event.edit("`Give me a user ID, username or reply!`")
        return

    userid = user_entity.id
    username = user_entity.username
    userfullname = f"{user_entity.first_name} {user_entity.last_name or ''}"

    await event.edit(f"**Full Name:** {userfullname}\n**Username:** @{username}\n**User ID:** {userid}")
