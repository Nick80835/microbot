import io

from PIL import Image, ImageOps
from telethon.types import MessageMediaPhoto, MessageMediaDocument

from ubot import ldr


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


@ldr.add("dcid")
async def datacenteridgetter(event):
    sender = await event.get_sender()
    reply = await event.get_reply_message()
    sender_dc_id = "Unknown (No photo.)"
    other_dc_id = ""

    if sender and sender.photo:
        sender_dc_id = f"`{sender.photo.dc_id}`"

    if event.media:
        if isinstance(event.media, MessageMediaPhoto):
            other_dc_id += f"\nUploaded photo DC ID: `{event.media.photo.dc_id}`"
        elif isinstance(event.media, MessageMediaDocument):
            other_dc_id += f"\nUploaded document DC ID: `{event.media.document.dc_id}`"
        else:
            other_dc_id += "\nUploaded media DC ID: Unknown"

    if reply:
        reply_sender = await reply.get_sender()

        if reply_sender and reply_sender.id != event.sender_id:
            if reply_sender.photo:
                other_dc_id += f"\nReplied sender DC ID: `{reply_sender.photo.dc_id}`"
            else:
                other_dc_id += f"\nReplied sender DC ID: Unknown (No photo.)"

        if reply.media:
            if isinstance(reply.media, MessageMediaPhoto):
                other_dc_id += f"\nReplied photo DC ID: `{reply.media.photo.dc_id}`"
            elif isinstance(reply.media, MessageMediaDocument):
                other_dc_id += f"\nReplied document DC ID: `{reply.media.document.dc_id}`"
            else:
                other_dc_id += f"\nReplied media DC ID: Unknown"

    await event.reply(
        f"Your DC ID: {sender_dc_id}" + other_dc_id
    )


@ldr.add("stickpng", help="Converts stickers to PNG files.")
async def stickertopng(event):
    sticker = await event.get_sticker()

    if not sticker:
        await event.reply("Reply to a sticker to get it as a PNG file!")
        return

    sticker_webp_io = io.BytesIO()
    await event.client.download_media(sticker, sticker_webp_io)
    await event.reply(file=await ldr.run_async(stickertopngsync, sticker_webp_io), force_document=True)


def stickertopngsync(sticker_webp_io):
    sticker_webp = Image.open(sticker_webp_io)
    sticker_png_io = io.BytesIO()
    sticker_webp.save(sticker_png_io, "PNG")
    sticker_png_io.name = "sticker.png"
    sticker_png_io.seek(0)

    return sticker_png_io


@ldr.add("stickflip", help="Flips stickers horizontally.")
async def flipsticker(event):
    sticker = await event.get_sticker()

    if not sticker:
        await event.reply("Reply to a sticker to flip that bitch!")
        return

    sticker_webp_io = io.BytesIO()
    await event.client.download_media(sticker, sticker_webp_io)
    await event.reply(file=await ldr.run_async(flipstickersync, sticker_webp_io))


def flipstickersync(sticker_webp_io):
    sticker_webp = Image.open(sticker_webp_io)
    sticker_webp = ImageOps.mirror(sticker_webp)
    sticker_flipped_io = io.BytesIO()
    sticker_webp.save(sticker_flipped_io, "WebP")
    sticker_flipped_io.name = "sticker.webp"
    sticker_flipped_io.seek(0)

    return sticker_flipped_io


@ldr.add("stickimg", help="Converts images to sticker sized PNG files.")
async def createsticker(event):
    data = await event.get_image()

    if not data:
        await event.reply("Reply to or caption an image to make it sticker-sized!")
        return

    image_io = io.BytesIO()
    await event.client.download_media(data, image_io)
    await event.reply(file=await ldr.run_async(createstickersync, image_io), force_document=True)


def createstickersync(image_io):
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

    return sticker_new_io
