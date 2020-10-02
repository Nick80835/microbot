# SPDX-License-Identifier: GPL-2.0-or-later

import io

from PIL import Image

from ubot import ldr

NEKO_URL = "https://nekos.life/api/v2/img/"
NEKO_TYPES_NSFW = ['lewd', 'tits', 'trap', 'anal', 'gasm', 'spank', 'feet', 'blowjob']
NEKO_TYPES = ['neko', 'smug', 'cuddle', 'hug', 'goose', 'waifu', 'slap', 'pat', 'woof', 'baka', 'kiss']
REPLY_TYPES = ['cuddle', 'hug', 'slap', 'spank', 'pat', 'baka', 'kiss', 'blowjob']


@ldr.add_list(NEKO_TYPES_NSFW, nsfw=True, pattern_extra="(f|)", userlocking=True)
@ldr.add_list(NEKO_TYPES, pattern_extra="(f|)", userlocking=True)
async def supernekoatsume(event):
    nekotype = event.command.lower()
    as_file = bool(event.other_args[0])

    if nekotype in REPLY_TYPES:
        reply_to = await event.get_reply_message() or event
    else:
        reply_to = event

    async with ldr.aioclient.get(NEKO_URL + nekotype) as response:
        if response.status == 200:
            image_url = (await response.json())["url"]
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    try:
        await event.client.send_file(event.peer_id, file=image_url, force_document=as_file, reply_to=reply_to)
    except:
        await event.reply(f"Failed to fetch media for query: **{nekotype}**")


@ldr.add("8ball")
async def eightball(event):
    async with ldr.aioclient.get(NEKO_URL + "8ball") as response:
        if response.status == 200:
            image_url = (await response.json())["url"]
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    async with ldr.aioclient.get(image_url) as response:
        if response.status == 200:
            image_data = await response.read()
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    sticker_image = Image.open(io.BytesIO(image_data))
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "WebP", quality=99)
    sticker_io.seek(0)
    sticker_io.name = "sticker.webp"

    try:
        await event.reply(file=sticker_io)
    except:
        await event.reply(f"Failed to send 8ball! :(")
