# SPDX-License-Identifier: GPL-2.0-or-later

import inspect
import io
from re import sub

from gtts import gTTS
from PIL import Image, ImageOps
from speedtest import Speedtest

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add("speed", sudo=True)
async def iamspeed(event):
    speed_message = await event.reply("`Running speed test…`")
    test = Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    await speed_message.edit(
        f"`Started at: {result['timestamp']}\n"
        f"Download: {speed_convert(result['download'])}\n"
        f"Upload: {speed_convert(result['upload'])}\n"
        f"Ping: {result['ping']} milliseconds\n"
        f"ISP: {result['client']['isp']}`"
    )


def speed_convert(size):
    power = 2**10
    zero = 0
    units = {0: '', 1: 'Kilobits/s', 2: 'Megabits/s', 3: 'Gigabits/s', 4: 'Terabits/s'}
    while size > power:
        size /= power
        zero += 1
    return f"{round(size, 2)} {units[zero]}"


@ldr.add("tts")
async def text_to_speech(event):
    text, reply = await ldr.get_text(event, return_msg=True)

    if not text:
        await event.reply("`Give me text or reply to text to use TTS.`")
        return

    tts_bytesio = io.BytesIO()
    tts_bytesio.name = "tts.mp3"

    try:
        tts = gTTS(text, lang="EN")
        tts.write_to_fp(tts_bytesio)
        tts_bytesio.seek(0)
    except AssertionError:
        await event.reply('`The text is empty.\n'
                         'Nothing left to speak after pre-precessing, '
                         'tokenizing and cleaning.`')
        return
    except RuntimeError:
        await event.reply('`Error loading the languages dictionary.`')
        return

    await event.client.send_file(event.chat_id, tts_bytesio, voice_note=True, reply_to=reply)


@ldr.add("ip")
async def ip_lookup(event):
    ip = await ldr.get_text(event)

    if not ip:
        await event.reply("`Provide an IP!`")
        return

    async with ldr.aioclient.get(f"http://ip-api.com/json/{ip}") as response:
        if response.status == 200:
            lookup_json = await response.json()
        else:
            await event.reply(f"`An error occurred when looking for `**{ip}**`: `**{response.status}**")
            return

    fixed_lookup = {}

    for key, value in lookup_json.items():
        special = {"lat": "Latitude", "lon": "Longitude", "isp": "ISP", "as": "AS", "asname": "AS name"}
        if key in special:
            fixed_lookup[special[key]] = str(value)
            continue

        key = sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", key)
        key = key.capitalize()

        if not value:
            value = "None"

        fixed_lookup[key] = str(value)

    text = ""

    for key, value in fixed_lookup.items():
        text = text + f"**{key}:** `{value}`\n"

    await event.reply(text)


@ldr.add("chatid")
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


@ldr.add("userid")
async def useridgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.from_id
    else:
        user_id = event.from_id

    await event.reply(f"**User ID:**` {user_id}`")


@ldr.add("profile")
async def userprofilegetter(event):
    if event.args:
        try:
            user_entity = await event.client.get_entity(event.args)
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


@ldr.add("stickpng")
async def stickertopng(event):
    reply = await event.get_reply_message()

    if reply and reply.sticker:
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


@ldr.add("stickflip")
async def flipsticker(event):
    reply = await event.get_reply_message()

    if reply and reply.sticker:
        sticker_webp_data = reply.sticker
    else:
        await event.reply("`Reply to a sticker to flip that bitch!`")
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
