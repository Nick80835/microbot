# SPDX-License-Identifier: GPL-2.0-or-later

import inspect
import io
from re import sub

from gtts import gTTS
from PIL import Image
from requests import get
from speedtest import Speedtest

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="speed", sudo=True)
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


@ldr.add(pattern="tts")
async def text_to_speech(event):
    message, reply = await get_text_arg(event)

    if not message or message == "":
        await event.reply("`Give me text or reply to text to use TTS.`")
        return

    tts_bytesio = io.BytesIO()
    tts_bytesio.name = "tts.mp3"

    try:
        tts = gTTS(message, lang="EN")
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

    await event.client.send_file(event.chat_id, tts_bytesio, voice_note=True, reply_to=reply or event)


@ldr.add(pattern="ip")
async def ip_lookup(event):
    ip, _ = await get_text_arg(event)

    if not ip:
        await event.reply("`Provide an IP!`")
        return

    lookup_json = get(f"http://ip-api.com/json/{ip}").json()
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


async def get_text_arg(event):
    text_arg = event.args
    reply = None

    if text_arg:
        pass
    elif event.is_reply:
        reply = await event.get_reply_message()
        text_arg = reply.text
    else:
        text_arg = None

    return text_arg, reply
