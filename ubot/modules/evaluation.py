# SPDX-License-Identifier: GPL-2.0-or-later

import inspect
import io
from re import sub

import wikipedia
from gtts import gTTS
from PIL import Image
from requests import get
from speedtest import Speedtest

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader
tts_lang = "EN"


@ldr.add(pattern="speed")
async def iamspeed(event):
    await event.edit("`Running speed test…`")
    test = Speedtest()

    test.get_best_server()
    test.download()
    test.upload()
    test.results.share()
    result = test.results.dict()

    await event.edit(
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


@ldr.add(pattern="lang")
async def set_lang(event):
    global tts_lang
    tts_lang = event.pattern_match.group(1)
    await event.edit(f"`Default language changed to `**{tts_lang}**")


@ldr.add(pattern="tts")
async def text_to_speech(event):
    await event.edit("`Processing…`")
    message, reply = await get_text_arg(event)

    if not message or message == "":
        await event.edit("`Give me text or reply to text to use TTS.`")
        return

    tts_bytesio = io.BytesIO()
    tts_bytesio.name = "tts.mp3"

    try:
        tts = gTTS(message, lang=tts_lang)
        tts.write_to_fp(tts_bytesio)
        tts_bytesio.seek(0)
    except AssertionError:
        await event.edit('`The text is empty.\n'
                         'Nothing left to speak after pre-precessing, '
                         'tokenizing and cleaning.`')
        return
    except ValueError:
        await event.edit('`Language is not supported.`')
        return
    except RuntimeError:
        await event.edit('`Error loading the languages dictionary.`')
        return

    await event.client.send_file(event.chat_id, tts_bytesio, voice_note=True, reply_to=reply)
    await event.delete()

@ldr.add(pattern="ip")
async def ip_lookup(event):
    ip, _ = await get_text_arg(event)

    if not ip:
        await event.edit("`Provide an IP!`")
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

    await event.edit(text)


@ldr.add(pattern="wiki")
async def wiki_cmd(event):
    query, _ = await get_text_arg(event)

    if not query:
        await event.edit("`You didn't specify what to search for!`")
        return
    
    await event.edit("`Processing…`")

    wiki_results = wikipedia.search(query)

    text = f"**Results for:**` {query}`\n\n"

    for result in wiki_results:
        try:
            text +=  f"`> `[{result}]({wikipedia.page(result).url})\n"
        except:
            pass

    await event.edit(text)


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
    reply = await event.get_reply_message()

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


@ldr.add(pattern="stickpng")
async def stickertopng(event):
    await event.edit("`Getting sticker as PNG…`")
    reply = await event.get_reply_message()

    if reply.sticker:
        sticker_webp_data = reply.sticker
    else:
        await event.edit("`Reply to a sticker to get it as a PNG file!`")
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
    text_arg = event.pattern_match.group(1)
    reply = None

    if text_arg:
        pass
    elif event.is_reply:
        reply = await event.get_reply_message()
        text_arg = reply.text
    else:
        text_arg = None

    return text_arg, reply
