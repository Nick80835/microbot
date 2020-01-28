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
import io

from PIL import Image

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="chatid")
async def chatidgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.forward and reply.forward.channel_id:
            await event.reply(f"**Channel ID:**` {reply.forward.channel_id}`")
            return
        chat_id = reply.chat_id
    else:
        chat_id = event.chat_id

    await event.reply(f"**Chat ID:**` {chat_id}`")


@ldr.add(pattern="userid")
async def useridgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.from_id
    else:
        user_id = event.from_id

    await event.reply(f"**User ID:**` {user_id}`")


@ldr.add(pattern="profile")
async def userprofilegetter(event):
    user_arg = event.pattern_match.group(1)

    if user_arg:
        try:
            user_entity = await event.client.get_entity(user_arg)
        except (ValueError, TypeError):
            await event.reply("`The ID or username you provided was invalid!`")
            return
    elif event.is_reply:
        reply = await event.get_reply_message()
        reply_id = reply.from_id
        if reply_id:
            try:
                user_entity = await event.client.get_entity(reply_id)
            except (ValueError, TypeError):
                await event.reply("`There was an error getting the user!`")
                return
        else:
            await event.reply("`The user may have super sneaky privacy settings enabled!`")
            return
    else:
        await event.reply("`Give me a user ID, username or reply!`")
        return

    userid = user_entity.id
    username = user_entity.username
    userfullname = f"{user_entity.first_name} {user_entity.last_name or ''}"

    await event.reply(f"**Full Name:** {userfullname}\n**Username:** @{username}\n**User ID:** {userid}")


@ldr.add(pattern="stickpng")
async def stickertopng(event):
    reply = await event.get_reply_message()

    if reply.sticker:
        sticker_webp_data = reply.sticker
    else:
        await event.reply("`Reply to a sticker to get it as a PNG file!`")
        return

    sticker_webp_io = io.BytesIO()
    await event.client.download_media(sticker_webp_data, sticker_webp_io)
    sticker_webp = Image.open(sticker_webp_io)
    sticker_png_io = io.BytesIO()
    sticker_webp.save(sticker_png_io, "PNG")
    sticker_png_io.name = "sticker.png"
    sticker_png_io.seek(0)

    await event.reply(file=sticker_png_io, force_document=True)
