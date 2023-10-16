import io
import re

from PIL import Image

from ubot import ldr


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

    await event.reply(file=await ldr.run_async(pokemon_image_sync, sprite_io))


def pokemon_image_sync(sprite_io):
    sticker_image = Image.open(io.BytesIO(sprite_io))
    sticker_image = sticker_image.crop(sticker_image.getbbox())

    final_width = 512
    final_height = 512

    if sticker_image.width > sticker_image.height:
        final_height = 512 * (sticker_image.height / sticker_image.width)
    elif sticker_image.width < sticker_image.height:
        final_width = 512 * (sticker_image.width / sticker_image.height)

    sticker_image = sticker_image.resize((int(final_width), int(final_height)), Image.NEAREST)
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "WebP", quality=99)
    sticker_io.seek(0)
    sticker_io.name = "sticker.webp"

    return sticker_io


@ldr.add("ip", help="IP lookup.")
async def ip_lookup(event):
    ip = await event.get_text()

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
            "Global Corona stats\n",
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

        return [{"title": "Corona Stats", "description": response['country'], "text": "\n".join(response_list)}]
    else:
        async with ldr.aioclient.get("https://disease.sh/v3/covid-19/all", headers={"accept": "application/json"}) as response:
            if response.status == 200:
                response = await response.json()
            else:
                return

        response_list = [
            "Global Corona stats\n",
            f"**Cases**\n   {response['cases']} total\n   {response['todayCases']} today\n   {response['active']} active\n   {round(response['cases'] / response['population'] * 100, 2)}% of population",
            f"**Tests**\n   {response['tests']} total\n   {round(response['cases'] / response['tests'] * 100, 2) if response['tests'] != 0 else 0.0}% positive\n   {round(response['tests'] / response['population'] * 100, 2)}% of population",
            f"**Deaths**\n   {response['deaths']} total\n   {response['todayDeaths']} today\n   {round(response['deaths'] / response['cases'] * 100, 2) if response['cases'] != 0 else 0.0}% of cases\n   {round(response['deaths'] / response['population'] * 100, 2)}% of population",
            f"**Recoveries**\n   {response['recovered']} total"
        ]

        return [{"title": "Corona Stats", "description": "Global", "text": "\n".join(response_list)}]
