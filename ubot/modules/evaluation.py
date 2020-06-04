# SPDX-License-Identifier: GPL-2.0-or-later

import asyncio
import inspect
import io
from re import sub

import wikipedia
from gtts import gTTS
from PIL import Image, ImageOps
from speedtest import Speedtest

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader
tts_lang = "EN"


@ldr.add("speed")
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


@ldr.add("lang")
async def set_lang(event):
    global tts_lang
    tts_lang = event.args
    await event.edit(f"`Default language changed to `**{event.args}**")


@ldr.add("tts")
async def text_to_speech(event):
    await event.edit("`Processing…`")
    text, reply = await ldr.get_text(event, return_msg=True)

    if not text:
        await event.edit("`Give me text or reply to text to use TTS.`")
        return

    tts_bytesio = io.BytesIO()
    tts_bytesio.name = "tts.mp3"

    try:
        tts = gTTS(text, lang=tts_lang)
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


@ldr.add("ip")
async def ip_lookup(event):
    ip = await ldr.get_text(event)

    if not ip:
        await event.edit("`Provide an IP!`")
        return

    async with ldr.aioclient.get(f"http://ip-api.com/json/{ip}") as response:
        if response.status == 200:
            lookup_json = await response.json()
        else:
            await event.edit(f"`An error occurred when looking for `**{ip}**`: `**{response.status}**")
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

    await event.edit(text)


@ldr.add("wiki")
async def wiki_cmd(event):
    query = await ldr.get_text(event)

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


@ldr.add("b2d")
async def bintodec(event):
    if not event.args:
        await event.edit("`Give me a binary number!`")
        return

    try:
        decimal = int(event.args, 2)
    except ValueError:
        await event.edit("`Give me a binary number!`")
        return

    await event.edit(f"**{event.args}** `=` **{decimal}**")


@ldr.add("d2b")
async def dectobin(event):
    try:
        decimal = int(event.args)
    except ValueError:
        await event.edit("`Give me a decimal number!`")
        return

    if not decimal:
        await event.edit("`Give me a decimal number!`")
        return

    binary = bin(decimal).replace("0b","")

    await event.edit(f"**{decimal}** `=` **{binary}**")


@ldr.add("eval")
async def evaluate(event):
    await event.edit("`Processing…`")
    reply = await event.get_reply_message()

    if not event.args:
        await event.edit("`Give me code to run!`")
        return

    try:
        eval_ret = eval(event.args)
    except Exception as exception:
        eval_ret = exception

    if inspect.isawaitable(eval_ret):
        isawait = " (awaited)"
        eval_ret = await eval_ret
    else:
        isawait = ""

    if len(f"**Evaluation:**\n`{event.args}`\n**Return{isawait}:**\n`{eval_ret}`") > 4096:
        text_io = io.BytesIO(str(eval_ret).encode("utf-8"))
        text_io.name = "return.txt"
        await event.edit("`Output too large for a message, sending as a file…`")
        await event.reply(file=text_io)
        return

    await event.edit(f"**Evaluation:**\n`{event.args}`\n**Return{isawait}:**\n`{eval_ret}`")


@ldr.add("chatid")
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


@ldr.add("userid")
async def useridgetter(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        user_id = reply.from_id
    else:
        user_id = event.from_id

    await event.edit(f"**User ID:**` {user_id}`")


@ldr.add("profile")
async def userprofilegetter(event):
    if event.args:
        try:
            user_entity = await event.client.get_entity(event.args)
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


@ldr.add("stickpng")
async def stickertopng(event):
    await event.edit("`Getting sticker as PNG…`")
    reply = await event.get_reply_message()

    if reply and reply.sticker:
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


@ldr.add("stickflip")
async def flipsticker(event):
    await event.edit("`Flipping this bitch…`")
    reply = await event.get_reply_message()

    if reply and reply.sticker:
        sticker_webp_data = reply.sticker
    else:
        await event.edit("`Reply to a sticker to flip that bitch!`")
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


@ldr.add("stickimg")
async def createsticker(event):
    await event.edit("`Creating sticker PNG…`")

    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await ldr.get_image(reply_message)

        if not data:
            await event.edit("`Reply to or caption an image to make it sticker-sized!`")
            return
    else:
        data = await ldr.get_image(event)

        if not data:
            await event.edit("`Reply to or caption an image to make it sticker-sized!`")
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
    await event.edit("`Compressing this bitch…`")
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
        await event.edit("`Reply to a sticker to compress that bitch!`")
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


@ldr.add("eiter")
async def edit_iterator(event):
    for i in range(45):
        await asyncio.sleep(0.08)
        try:
            await event.edit(f"`{i}`")
        except:
            pass
