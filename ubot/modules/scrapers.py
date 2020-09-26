# SPDX-License-Identifier: GPL-2.0-or-later

import io
import os
import re
from time import time_ns

import pafy
from gtts import gTTS
from howdoi import howdoi
from PIL import Image
from telethon.tl.types import DocumentAttributeVideo

from ubot.fixes.fast_telethon import upload_file
from ubot.fixes.parallel_download import download
from ubot import ldr

os.environ["HOWDOI_SEARCH_ENGINE"] = "bing"


@ldr.add("dadjoke", help="Fetches the most funny shit you've ever read.")
async def dadjoke(event):
    async with ldr.aioclient.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}) as response:
        if response.status == 200:
            dad_joke = (await response.json())["joke"]
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return

    await event.reply(dad_joke)


@ldr.add("fact", help="Fetches random facts.")
async def randomfact(event):
    async with ldr.aioclient.get("https://uselessfacts.jsph.pl/random.json", params={"language": "en"}) as response:
        if response.status == 200:
            random_fact = (await response.json())["text"].replace("`", "'")
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return

    await event.reply(random_fact)


@ldr.add("fakeword", help="Fetches random fake words.")
async def fakeword(event):
    async with ldr.aioclient.get("https://www.thisworddoesnotexist.com/api/random_word.json") as response:
        if response.status == 200:
            random_word_json = (await response.json())["word"]
            word = random_word_json["word"]
            definition = random_word_json["definition"]
            example = random_word_json["example"]
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return

    await event.reply(f"**{word}:** __{definition}__\n\n**Example:** __{example}__")


@ldr.add("pokemon", pattern_extra="(s|)", help="Fetches Pokemon sprites, requires a name or ID as an argument.")
async def pokemon_image(event):
    if not event.args:
        await event.reply("Specify a Pokémon name!")
        return

    async with ldr.aioclient.get("https://pokeapi.co/api/v2/pokemon/" + event.args) as response:
        if response.status == 200:
            sprite_url = (await response.json())["sprites"]["front_shiny" if event.other_args[0] else "front_default"]
        else:
            await event.reply(f"An error occurred: **{response.status}**")
            return

    if not sprite_url:
        await event.reply("That Pokémon config doesnt have an available sprite!")
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
        await event.reply(f"Syntax: {ldr.prefix()}hdi <question>")
        return

    response = howdoi.howdoi(vars(howdoi.get_parser().parse_args(event.args.split(' '))))
    response = re.sub(r'\n\n+', '\n\n', response).strip()

    await event.reply(f"**Query:**\n{event.args}\n**Answer:**\n{response}")


@ldr.add("tts", help="Text to speech.")
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


@ldr.add("ip", help="IP lookup.")
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


@ldr.add("corona", help="Fetches Coronavirus stats, takes an optional country name as an argument.")
async def corona(event):
    if event.args:
        async with ldr.aioclient.get(f"https://disease.sh/v3/covid-19/countries/{event.args}", headers={"accept": "application/json"}) as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.reply(f"An error occurred, response code: **{response.status}**")
                return

        response_list = [
            f"Corona stats for **{response['country']}**\n",
            f"**Cases**\n   {response['cases']} total\n   {response['todayCases']} today\n   {response['active']} active\n   {round(response['cases'] / response['population'] * 100, 2)}% of population",
            f"**Tests**\n   {response['tests']} total\n   {round(response['cases'] / response['tests'] * 100, 2) if response['tests'] != 0 else 0.0}% positive\n   {round(response['tests'] / response['population'] * 100, 2)}% of population",
            f"**Deaths**\n   {response['deaths']} total\n   {response['todayDeaths']} today\n   {round(response['deaths'] / response['cases'] * 100, 2) if response['cases'] != 0 else 0.0}% of cases\n   {round(response['deaths'] / response['population'] * 100, 2)}% of population",
            f"**Recoveries**\n   {response['recovered']} total"
        ]

        await event.reply("\n".join(response_list))
    else:
        async with ldr.aioclient.get("https://disease.sh/v3/covid-19/all", headers={"accept": "application/json"}) as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.reply(f"`An error occurred, response code: `**{response.status}**")
                return

        response_list = [
            f"Global Corona stats\n",
            f"**Cases**\n   {response['cases']} total\n   {response['todayCases']} today\n   {response['active']} active\n   {round(response['cases'] / response['population'] * 100, 2)}% of population",
            f"**Tests**\n   {response['tests']} total\n   {round(response['cases'] / response['tests'] * 100, 2) if response['tests'] != 0 else 0.0}% positive\n   {round(response['tests'] / response['population'] * 100, 2)}% of population",
            f"**Deaths**\n   {response['deaths']} total\n   {response['todayDeaths']} today\n   {round(response['deaths'] / response['cases'] * 100, 2) if response['cases'] != 0 else 0.0}% of cases\n   {round(response['deaths'] / response['population'] * 100, 2)}% of population",
            f"**Recoveries**\n   {response['recovered']} total"
        ]

        await event.reply("\n".join(response_list))


@ldr.add_inline_article("corona", default="corona")
async def corona_inline(event):
    if event.args:
        async with ldr.aioclient.get(f"https://disease.sh/v3/covid-19/countries/{event.args}", headers={"accept": "application/json"}) as response:
            if response.status == 200:
                response = await response.json()
            else:
                return

        response_list = [
            f"Corona stats for **{response['country']}**\n",
            f"**Cases**\n   {response['cases']} total\n   {response['todayCases']} today\n   {response['active']} active\n   {round(response['cases'] / response['population'] * 100, 2)}% of population",
            f"**Tests**\n   {response['tests']} total\n   {round(response['cases'] / response['tests'] * 100, 2) if response['tests'] != 0 else 0.0}% positive\n   {round(response['tests'] / response['population'] * 100, 2)}% of population",
            f"**Deaths**\n   {response['deaths']} total\n   {response['todayDeaths']} today\n   {round(response['deaths'] / response['cases'] * 100, 2) if response['cases'] != 0 else 0.0}% of cases\n   {round(response['deaths'] / response['population'] * 100, 2)}% of population",
            f"**Recoveries**\n   {response['recovered']} total"
        ]

        return [{"title": f"Corona Stats", "description": response['country'], "text": "\n".join(response_list)}]
    else:
        async with ldr.aioclient.get("https://disease.sh/v3/covid-19/all", headers={"accept": "application/json"}) as response:
            if response.status == 200:
                response = await response.json()
            else:
                return

        response_list = [
            f"Global Corona stats\n",
            f"**Cases**\n   {response['cases']} total\n   {response['todayCases']} today\n   {response['active']} active\n   {round(response['cases'] / response['population'] * 100, 2)}% of population",
            f"**Tests**\n   {response['tests']} total\n   {round(response['cases'] / response['tests'] * 100, 2) if response['tests'] != 0 else 0.0}% positive\n   {round(response['tests'] / response['population'] * 100, 2)}% of population",
            f"**Deaths**\n   {response['deaths']} total\n   {response['todayDeaths']} today\n   {round(response['deaths'] / response['cases'] * 100, 2) if response['cases'] != 0 else 0.0}% of cases\n   {round(response['deaths'] / response['population'] * 100, 2)}% of population",
            f"**Recoveries**\n   {response['recovered']} total"
        ]

        return [{"title": f"Corona Stats", "description": "Global", "text": "\n".join(response_list)}]


@ldr.add("yt", userlocking=True)
async def youtube_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbest(preftype="mp4")

    try:
        cache_required, file_size = await ldr.cache.is_cache_required(video_stream.url)

        if cache_required:
            if file_size >= 1000000000:
                await event.reply(f"File too large to send ({int(file_size / 1000000)}MB), sorry about that.")
                return

            wait_msg = await event.reply(f"Large file detected ({int(file_size / 1000000)}MB), this may take some time…")

            start_time = time_ns()
            file_path = await download(video_stream.url, f"{event.chat_id}_{event.id}", ldr.aioclient)
            end_time = time_ns()

            time_taken_seconds = int((end_time - start_time) / 1000000000) or 1
            speed = int(int(file_size / 1000000) / time_taken_seconds)

            await wait_msg.edit(f"Download complete, took {time_taken_seconds} seconds at ~{speed}MB/s")

            file_handle = await upload_file(event.client, file_path)

            await event.client.send_file(event.chat, file=file_handle, reply_to=event, attributes=[
                DocumentAttributeVideo(
                    duration=video.length,
                    w=video_stream.dimensions[0],
                    h=video_stream.dimensions[1],
                    supports_streaming=True
                )])

            await wait_msg.delete()

            ldr.cache.remove_cache(file_path)
        else:
            await event.reply(file=video_stream.url)
    except:
        try:
            ldr.cache.remove_cache(file_path)
        except:
            pass

        await event.reply(f"Download failed: [URL]({video_stream.url})")


@ldr.add("yta", userlocking=True)
async def youtube_audio_cmd(event):
    video = pafy.new(event.args)
    audio_stream = video.getbestaudio(preftype="m4a")

    try:
        async with ldr.aioclient.get(audio_stream.url) as response:
            if response.status == 200:
                audio_data = io.BytesIO(await response.read())
                audio_data.name = "audio.m4a"
            else:
                raise Exception

        await event.reply(file=audio_data)
    except:
        await event.reply(f"Download failed: [URL]({audio_stream.url})")
