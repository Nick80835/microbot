# SPDX-License-Identifier: GPL-2.0-or-later

import io
import os
import re

import pafy
from gtts import gTTS
from howdoi import howdoi
from PIL import Image

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader
os.environ["HOWDOI_SEARCH_ENGINE"] = "bing"


@ldr.add("dadjoke")
async def dadjoke(event):
    async with ldr.aioclient.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}) as response:
        if response.status == 200:
            dad_joke = (await response.json())["joke"]
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return

    await event.reply(dad_joke)


@ldr.add("fact")
async def randomfact(event):
    async with ldr.aioclient.get("https://uselessfacts.jsph.pl/random.json", params={"language": "en"}) as response:
        if response.status == 200:
            random_fact = (await response.json())["text"].replace("`", "'")
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return

    await event.reply(random_fact)


@ldr.add("pokemon(s|)")
async def pokemon_image(event):
    if not event.args:
        await event.reply("Specify a Pokémon name!")
        return

    async with ldr.aioclient.get("https://pokeapi.co/api/v2/pokemon/" + event.args) as response:
        if response.status == 200:
            sprite_url = (await response.json())["sprites"]["front_shiny" if event.pattern_match.group(1) else "front_default"]
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return
    
    async with ldr.aioclient.get(sprite_url) as response:
        if response.status == 200:
            sprite_io = await response.read()
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return

    sticker_image = Image.open(io.BytesIO(sprite_io))
    sticker_image = sticker_image.crop(sticker_image.getbbox())
    sticker_image = sticker_image.resize((sticker_image.size[0]*4, sticker_image.size[1]*4), Image.NEAREST)
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "WebP", quality=99)
    sticker_io.seek(0)
    sticker_io.name = "sticker.webp"

    await event.reply(file=sticker_io)


@ldr.add("hdi")
async def howdoi_cmd(event):
    if not event.args:
        await event.reply(f"Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}hdi <question>")
        return

    response = howdoi.howdoi(vars(howdoi.get_parser().parse_args(event.args.split(' '))))
    response = re.sub(r'\n\n+', '\n\n', response).strip()

    await event.reply(f"**Query:**\n{event.args}\n**Answer:**\n{response}")


@ldr.add("tts")
async def text_to_speech(event):
    text, reply = await ldr.get_text(event, return_msg=True)

    if not text:
        await event.reply("Give me text or reply to text to use TTS.")
        return

    tts_bytesio = io.BytesIO()
    tts_bytesio.name = "tts.mp3"

    try:
        tts = gTTS(text, lang="EN")
        tts.write_to_fp(tts_bytesio)
        tts_bytesio.seek(0)
    except AssertionError:
        await event.reply('The text is empty.\nNothing left to speak after pre-precessing, tokenizing and cleaning.')
        return
    except RuntimeError:
        await event.reply('Error loading the languages dictionary.')
        return

    await event.client.send_file(event.chat_id, tts_bytesio, voice_note=True, reply_to=reply)


@ldr.add("ip")
async def ip_lookup(event):
    ip = await ldr.get_text(event)

    if not ip:
        await event.reply("Provide an IP!")
        return

    async with ldr.aioclient.get(f"http://ip-api.com/json/{ip}") as response:
        if response.status == 200:
            lookup_json = await response.json()
        else:
            await event.reply(f"An error occurred when looking for **{ip}**: **{response.status}**")
            return

    fixed_lookup = {}

    for key, value in lookup_json.items():
        special = {"lat": "Latitude", "lon": "Longitude", "isp": "ISP", "as": "AS", "asname": "AS name"}
        if key in special:
            fixed_lookup[special[key]] = str(value)
            continue

        key = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", key)
        key = key.capitalize()

        if not value:
            value = "None"

        fixed_lookup[key] = str(value)

    text = ""

    for key, value in fixed_lookup.items():
        text = text + f"**{key}:** {value}\n"

    await event.reply(text)


@ldr.add("corona")
async def corona(event):
    if event.args:
        async with ldr.aioclient.get(f"https://corona.lmao.ninja/v2/countries/{event.args}") as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.reply(f"An error occurred, response code: **{response.status}**")
                return

        response_text = f"Stats for **{response['country']}**\n\n**Cases:** {response['cases']} ({response['todayCases']} today)\n**Deaths:** {response['deaths']} ({response['todayDeaths']} today)\n**Recoveries:** {response['recovered']}"
        await event.reply(response_text)
    else:
        async with ldr.aioclient.get(f"https://corona.lmao.ninja/v2/all") as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.reply(f"`An error occurred, response code: `**{response.status}**")
                return

        response_text = f"Global stats\n\n**Cases:** {response['cases']} ({response['todayCases']} today)\n**Deaths:** {response['deaths']} ({response['todayDeaths']} today)\n**Recoveries:** {response['recovered']}"
        await event.reply(response_text)


@ldr.add("yt", userlocking=True)
async def youtube_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbest()
    try:
        await event.reply(file=video_stream.url)
    except:
        await event.reply(f"Download failed: [URL]({video_stream.url})")


@ldr.add("yta", userlocking=True)
async def youtube_audio_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbestaudio()
    try:
        await event.reply(file=video_stream.url)
    except:
        await event.reply(f"Download failed: [URL]({video_stream.url})")
