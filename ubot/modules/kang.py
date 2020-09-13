# SPDX-License-Identifier: GPL-2.0-or-later

import io
import urllib

from PIL import Image, ImageOps
from telethon.tl.types import DocumentAttributeFilename

from ubot import ldr

pack_full = "Whoa! That's probably enough stickers for one pack, give it a break. \
A pack can't have more than 120 stickers at the moment."


@ldr.add("kang", help="Kangs stickers and images.")
async def kang(event):
    await event.edit("`Kanging…`")
    reply = await event.get_reply_message()
    static_sticker = True
    from_image = False

    if reply:
        kang_image_data = await ldr.get_image(reply)

        if kang_image_data and not reply.document:
            from_image = True
            kang_emojis = event.args or "🤔"
        elif reply.document and DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply.media.document.attributes:
            static_sticker = False
            kang_image_data = reply.document
            kang_emojis =  reply.file.emoji or "🤔"
        elif reply.sticker and reply.document and DocumentAttributeFilename(file_name='sticker.webp') in reply.media.document.attributes:
            kang_emojis = reply.file.emoji or "🤔"
        elif kang_image_data:
            from_image = True
            kang_emojis = event.args or "🤔"
        else:
            await event.edit("`Reply to an image or sticker to kang it!`")
            return
    else:
        await event.edit("`Reply to an image or sticker to kang it!`")
        return

    image_io = io.BytesIO()
    await event.client.download_media(kang_image_data, image_io)

    if from_image:
        try:
            sticker_image = Image.open(image_io)
        except:
            await event.edit("`You can't kang that!`")
            return

        image_io = resize_image(sticker_image)
    elif static_sticker:
        sticker_image = Image.open(image_io)

        if sticker_image.width != 512 or sticker_image.height != 512:
            image_io = resize_image(sticker_image)
        else:
            image_io = io.BytesIO()
            sticker_image.save(image_io, "PNG")
            image_io.name = "sticker.png"
            image_io.seek(0)
    else:
        image_io.name = "sticker.tgs"
        image_io.seek(0)

    me = await event.client.get_me()
    pack_number = 1

    if not static_sticker:
        pack_nickname = f"@{me.username or me.first_name}'s kang pack {pack_number} animated"
        pack_name = f"a{me.id}_kangpack_{pack_number}_anim"
        cmd = '/newanimated'
    else:
        pack_nickname = f"@{me.username or me.first_name}'s kang pack {pack_number}"
        pack_name = f"a{me.id}_kangpack_{pack_number}"
        cmd = '/newpack'

    response = urllib.request.urlopen(urllib.request.Request(f'http://t.me/addstickers/{pack_name}'))
    htmlstr = response.read().decode("utf8").split('\n')

    if "  A <strong>Telegram</strong> user has created the <strong>Sticker&nbsp;Set</strong>." not in htmlstr:
        async with event.client.conversation('Stickers') as conv:
            await conv.send_message('/addsticker')
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(pack_name)
            sticker_response = await conv.get_response()

            while sticker_response.text == pack_full:
                pack_number += 1

                if not static_sticker:
                    pack_nickname = f"@{me.username or me.first_name}'s kang pack {pack_number} animated"
                    pack_name = f"a{me.id}_kangpack_{pack_number}_anim"
                else:
                    pack_nickname = f"@{me.username or me.first_name}'s kang pack {pack_number}"
                    pack_name = f"a{me.id}_kangpack_{pack_number}"

                await event.edit(f"`Switching to pack {pack_number} due to insufficient space.`")
                await conv.send_message(pack_name)
                sticker_response = await conv.get_response()

                if sticker_response.text == "Invalid pack selected.":
                    await conv.send_message(cmd)
                    await conv.get_response()
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await conv.send_message(pack_nickname)
                    await conv.get_response()
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await conv.send_file(image_io, force_document=True)
                    await conv.get_response()
                    await conv.send_message(kang_emojis)
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await conv.send_message("/publish")

                    if not static_sticker:
                        await conv.get_response()
                        await conv.send_message(f"<{pack_nickname}>")

                    await conv.get_response()
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await conv.send_message("/skip")
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await conv.send_message(pack_name)
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await conv.get_response()
                    await event.client.send_read_acknowledge(conv.chat_id)
                    await event.edit(f"`Sticker added in a different Pack! This pack is newly created! Your pack can be found `[here](t.me/addstickers/{pack_name})")
                    return

            await conv.send_file(image_io, force_document=True)
            await conv.get_response()
            await conv.send_message(kang_emojis)
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.get_response()
            await conv.send_message('/done')
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
    else:
        await event.edit("`Userbot sticker pack doesn't exist! Making a new one!`")
        async with event.client.conversation('Stickers') as conv:
            await conv.send_message(cmd)
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(pack_nickname)
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.send_file(image_io, force_document=True)
            await conv.get_response()
            await conv.send_message(kang_emojis)
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.get_response()
            await conv.send_message("/publish")

            if not static_sticker:
                await conv.get_response()
                await conv.send_message(f"<{pack_nickname}>")

            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.send_message("/skip")
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.get_response()
            await conv.send_message(pack_name)
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)

    await event.edit(f"`Sticker added! Your pack can be found `[here](t.me/addstickers/{pack_name})")


def resize_image(sticker_image):
    sticker_image = sticker_image.crop(sticker_image.getbbox())
    final_width = 512
    final_height = 512

    if sticker_image.width > sticker_image.height:
        final_height = 512 * (sticker_image.height / sticker_image.width)
    elif sticker_image.width < sticker_image.height:
        final_width = 512 * (sticker_image.width / sticker_image.height)

    sticker_image = ImageOps.fit(sticker_image, (int(final_width), int(final_height)))
    image_io = io.BytesIO()
    sticker_image.save(image_io, "PNG")
    image_io.name = "sticker.png"
    image_io.seek(0)

    return image_io
