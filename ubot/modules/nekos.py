import io

from PIL import Image
from telethon.tl.types import (InputMediaDocumentExternal,
                               InputMediaPhotoExternal)

from ubot import ldr

NEKO_URL = "https://nekos.life/api/v2/img/"
NEKO_TYPES_NSFW = ['lewd', 'gasm', 'spank']
NEKO_TYPES = ['neko', 'smug', 'cuddle', 'hug', 'goose', 'waifu', 'slap', 'pat', 'woof', 'kiss']
REPLY_TYPES = ['cuddle', 'hug', 'slap', 'spank', 'pat', 'kiss']


@ldr.add_list(NEKO_TYPES_NSFW, nsfw=True, pattern_extra="(f|)", userlocking=True)
@ldr.add_list(NEKO_TYPES, pattern_extra="(f|)", userlocking=True)
async def supernekoatsume(event):
    nekotype = event.object.pattern
    as_file = bool(event.other_args[0])

    if nekotype in REPLY_TYPES and event.is_reply:
        reply_to = await event.get_reply_message()
    else:
        reply_to = event

    async with ldr.aioclient.get(NEKO_URL + nekotype) as response:
        if response.status == 200:
            image_url = (await response.json())["url"]
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    try:
        if event.chat_db.spoiler_nsfw and event.object.nsfw:
            if as_file:
                file = InputMediaDocumentExternal(url=image_url, spoiler=True)
            else:
                file = InputMediaPhotoExternal(url=image_url, spoiler=True)
        else:
            file = image_url

        await event.respond(file=file, force_document=as_file, reply_to=reply_to)
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

    try:
        await event.reply(file=await ldr.run_async(eightballsync, image_data))
    except:
        await event.reply("Failed to send 8ball! :(")


def eightballsync(image_data):
    sticker_image = Image.open(io.BytesIO(image_data))
    sticker_image = sticker_image.resize((512, 512), Image.BILINEAR)
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "WebP", quality=99)
    sticker_io.seek(0)
    sticker_io.name = "sticker.webp"

    return sticker_io
