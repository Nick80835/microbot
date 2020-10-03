# SPDX-License-Identifier: GPL-2.0-or-later

import io

from PIL import Image, ImageOps
from speedtest import Speedtest

from ubot import ldr


@ldr.add("speed", owner=True, hide_help=True)
async def iamspeed(event):
    speed_message = await event.reply("Running speed test…")
    test = Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    await speed_message.edit(
        f"**Started at:** {result['timestamp']}\n"
        f"**Download:** {speed_convert(result['download'])}\n"
        f"**Upload:** {speed_convert(result['upload'])}\n"
        f"**Ping:** {result['ping']} milliseconds\n"
        f"**ISP:** {result['client']['isp']}"
    )


def speed_convert(size):
    power = 2**10
    zero = 0
    units = {0: '', 1: 'Kilobits/s', 2: 'Megabits/s', 3: 'Gigabits/s', 4: 'Terabits/s'}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@ldr.add("chatid")
async def chatidgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.forward and reply.forward.channel_id:
            await event.reply(f"**Channel ID:** {reply.forward.channel_id}")
            return
        chat_id = reply.chat_id
    else:
        chat_id = event.chat_id

    await event.reply(f"**Chat ID:** {chat_id}")


@ldr.add("userid")
async def useridgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.sender_id
    else:
        user_id = event.sender_id

    await event.reply(f"**User ID:** {user_id}")


@ldr.add("profile")
async def userprofilegetter(event):
    if event.args:
        try:
            user_entity = await event.client.get_entity(event.args)
        except (ValueError, TypeError):
            await event.reply("The ID or username you provided was invalid!")
            return
    elif event.is_reply:
        reply = await event.get_reply_message()
        reply_id = reply.sender_id
        if reply_id:
            try:
                user_entity = await event.client.get_entity(reply_id)
            except (ValueError, TypeError):
                await event.reply("There was an error getting the user!")
                return
        else:
            await event.reply("The user may have super sneaky privacy settings enabled!")
            return
    else:
        await event.reply("Give me a user ID, username or reply!")
        return

    userid = user_entity.id
    username = user_entity.username
    userfullname = f"{user_entity.first_name} {user_entity.last_name or ''}"

    await event.reply(f"**Full Name:** {userfullname}\n**Username:** @{username}\n**User ID:** {userid}")


@ldr.add("stickpng", help="Converts stickers to PNG files.")
async def stickertopng(event):
    reply = await event.get_reply_message()

    if reply and reply.sticker:
        sticker_webp_data = reply.sticker
    else:
        await event.reply("Reply to a sticker to get it as a PNG file!")
        return

    sticker_webp_io = io.BytesIO()
    await event.client.download_media(sticker_webp_data, sticker_webp_io)
    sticker_webp = Image.open(sticker_webp_io)
    sticker_png_io = io.BytesIO()
    sticker_webp.save(sticker_png_io, "PNG")
    sticker_png_io.name = "sticker.png"
    sticker_png_io.seek(0)

    await event.reply(file=sticker_png_io, force_document=True)


@ldr.add("stickflip", help="Flips stickers horizontally.")
async def flipsticker(event):
    reply = await event.get_reply_message()

    if reply and reply.sticker:
        sticker_webp_data = reply.sticker
    else:
        await event.reply("Reply to a sticker to flip that bitch!")
        return

    sticker_webp_io = io.BytesIO()
    await event.client.download_media(sticker_webp_data, sticker_webp_io)
    sticker_webp = Image.open(sticker_webp_io)
    sticker_webp = ImageOps.mirror(sticker_webp)
    sticker_flipped_io = io.BytesIO()
    sticker_webp.save(sticker_flipped_io, "WebP")
    sticker_flipped_io.name = "sticker.webp"
    sticker_flipped_io.seek(0)

    await event.reply(file=sticker_flipped_io)


@ldr.add("stickimg", help="Converts images to sticker sized PNG files.")
async def createsticker(event):
    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await ldr.get_image(reply_message)

        if not data:
            await event.reply("Reply to or caption an image to make it sticker-sized!")
            return
    else:
        data = await ldr.get_image(event)

        if not data:
            await event.reply("Reply to or caption an image to make it sticker-sized!")
            return

    image_io = io.BytesIO()
    await event.client.download_media(data, image_io)
    sticker_png = Image.open(image_io)
    sticker_png = sticker_png.crop(sticker_png.getbbox())

    final_width = 512
    final_height = 512

    if sticker_png.width > sticker_png.height:
        final_height = 512 * (sticker_png.height / sticker_png.width)
    elif sticker_png.width < sticker_png.height:
        final_width = 512 * (sticker_png.width / sticker_png.height)

    sticker_png = ImageOps.fit(sticker_png, (int(final_width), int(final_height)))
    sticker_new_io = io.BytesIO()
    sticker_png.save(sticker_new_io, "PNG")
    sticker_new_io.name = "sticker.png"
    sticker_new_io.seek(0)

    await event.reply(file=sticker_new_io, force_document=True)


@ldr.add("compress")
async def compressor(event):
    reply = await event.get_reply_message()

    try:
        compression_quality = int(event.args)
        if compression_quality < 0:
            compression_quality = 0
        elif compression_quality > 100:
            compression_quality = 100
    except ValueError:
        compression_quality = 15

    if reply and reply.sticker:
        sticker_webp_data = reply.sticker
    else:
        await event.reply("Reply to a sticker to compress that bitch!")
        return

    sticker_io = io.BytesIO()
    await event.client.download_media(sticker_webp_data, sticker_io)

    sticker_image = Image.open(sticker_io)
    sticker_image = sticker_image.convert("RGB")
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "JPEG", quality=compression_quality)
    sticker_image = Image.open(sticker_io)
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "WebP", quality=99)
    sticker_io.seek(0)
    sticker_io.name = "sticker.webp"

    await event.reply(file=sticker_io)
