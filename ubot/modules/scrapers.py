# SPDX-License-Identifier: GPL-2.0-or-later

import io
import os
import re

import pafy
import wikipedia
from gtts import gTTS
from howdoi import howdoi
from PIL import Image

from ubot import ldr

os.environ["HOWDOI_SEARCH_ENGINE"] = "bing"
tts_lang = "EN"


@ldr.add("dadjoke", help="Fetches the most funny shit you've ever read.")
async def dadjoke(event):
    async with ldr.aioclient.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}) as response:
        if response.status == 200:
            dad_joke = (await response.json())["joke"]
        else:
            await event.edit(f"An error occurred: **{response.status}**")
            return

    await event.edit(dad_joke)


@ldr.add("fact", help="Fetches random facts.")
async def randomfact(event):
    async with ldr.aioclient.get("https://uselessfacts.jsph.pl/random.json", params={"language": "en"}) as response:
        if response.status == 200:
            random_fact = (await response.json())["text"].replace("`", "'")
        else:
            await event.edit(f"An error occurred: **{response.status}**")
            return

    await event.edit(random_fact)


@ldr.add("fakeword", help="Fetches random fake words.")
async def fakeword(event):
    async with ldr.aioclient.get("https://www.thisworddoesnotexist.com/api/random_word.json") as response:
        if response.status == 200:
            random_word_json = (await response.json())["word"]
            word = random_word_json["word"]
            definition = random_word_json["definition"]
            example = random_word_json["example"]
        else:
            await event.edit(f"An error occurred: **{response.status}**")
            return

    await event.edit(f"**{word}:** __{definition}__\n\n**Example:** __{example}__")


@ldr.add("pokemon", pattern_extra="(s|)", help="Fetches Pokemon sprites, requires a name or ID as an argument.")
async def pokemon_image(event):
    if not event.args:
        await event.edit("Specify a Pokémon name!")
        return

    async with ldr.aioclient.get("https://pokeapi.co/api/v2/pokemon/" + event.args) as response:
        if response.status == 200:
            sprite_url = (await response.json())["sprites"]["front_shiny" if event.other_args[0] else "front_default"]
        else:
            await event.edit(f"An error occurred: **{response.status}**")
            return

    if not sprite_url:
        await event.edit("That Pokémon config doesnt have an available sprite!")
        return

    async with ldr.aioclient.get(sprite_url) as response:
        if response.status == 200:
            sprite_io = await response.read()
        else:
            await event.edit(f"An error occurred: **{response.status}**")
            return

    sticker_image = Image.open(io.BytesIO(sprite_io))
    sticker_image = sticker_image.crop(sticker_image.getbbox())
    sticker_image = sticker_image.resize((sticker_image.size[0]*4, sticker_image.size[1]*4), Image.NEAREST)
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "WebP", quality=99)
    sticker_io.seek(0)
    sticker_io.name = "sticker.webp"

    await event.client.send_file(event.chat, sticker_io)
    await event.delete()


@ldr.add("hdi")
async def howdoi_cmd(event):
    if not event.args:
        await event.edit(f"`Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}hdi <question>`")
        return

    response = howdoi.howdoi(vars(howdoi.get_parser().parse_args(event.args.split(' '))))
    response = re.sub(r'\n\n+', '\n\n', response).strip()

    await event.edit(f"**Query:**\n{event.args}\n**Answer:**\n{response}")


@ldr.add("lang")
async def set_lang(event):
    global tts_lang
    tts_lang = event.args
    await event.edit(f"`Default language changed to `**{event.args}**")


@ldr.add("tts", help="Text to speech.")
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


@ldr.add("ip", help="IP lookup.")
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

        key = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", key)
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


@ldr.add("corona", help="Fetches Coronavirus stats, takes an optional country name as an argument.")
async def corona(event):
    if event.args:
        async with ldr.aioclient.get(f"https://disease.sh/v3/covid-19/countries/{event.args}", headers={"accept": "application/json"}) as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.edit(f"`An error occurred, response code: `**{response.status}**")
                return

        response_list = [
            f"Corona stats for **{response['country']}**\n",
            f"**Cases**\n   {response['cases']} total\n   {response['todayCases']} today\n   {response['active']} active\n   {round(response['cases'] / response['population'] * 100, 2)}% of population",
            f"**Tests**\n   {response['tests']} total\n   {round(response['cases'] / response['tests'] * 100, 2)}% positive\n   {round(response['tests'] / response['population'] * 100, 2)}% of population",
            f"**Deaths**\n   {response['deaths']} total\n   {response['todayDeaths']} today\n   {round(response['deaths'] / response['cases'] * 100, 2)}% of cases\n   {round(response['deaths'] / response['population'] * 100, 2)}% of population",
            f"**Recoveries**\n   {response['recovered']} total"
        ]

        await event.edit("\n".join(response_list))
    else:
        async with ldr.aioclient.get("https://disease.sh/v3/covid-19/all", headers={"accept": "application/json"}) as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.edit(f"`An error occurred, response code: `**{response.status}**")
                return

        response_list = [
            f"Global Corona stats\n",
            f"**Cases**\n   {response['cases']} total\n   {response['todayCases']} today\n   {response['active']} active\n   {round(response['cases'] / response['population'] * 100, 2)}% of population",
            f"**Tests**\n   {response['tests']} total\n   {round(response['cases'] / response['tests'] * 100, 2)}% positive\n   {round(response['tests'] / response['population'] * 100, 2)}% of population",
            f"**Deaths**\n   {response['deaths']} total\n   {response['todayDeaths']} today\n   {round(response['deaths'] / response['cases'] * 100, 2)}% of cases\n   {round(response['deaths'] / response['population'] * 100, 2)}% of population",
            f"**Recoveries**\n   {response['recovered']} total"
        ]

        await event.edit("\n".join(response_list))


@ldr.add("yt")
async def youtube_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbest()
    try:
        await event.client.send_file(event.chat_id, file=video_stream.url)
    except:
        await event.reply(f"`Download failed: `[URL]({video_stream.url})")


@ldr.add("yta")
async def youtube_audio_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbestaudio()
    try:
        await event.client.send_file(event.chat_id, file=video_stream.url)
    except:
        await event.reply(f"`Download failed: `[URL]({video_stream.url})")
