# SPDX-License-Identifier: GPL-2.0-or-later

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

NEKO_URL = "https://nekos.life/api/v2/img/"
NEKO_TYPES = "neko|lewd|smug|tits|trap|anal|cuddle|hug|goose|waifu|gasm|slap|spank|pat|feet|woof"


@ldr.add(f"({NEKO_TYPES})(f|)")
async def supernekoatsume(event):
    nekotype = event.pattern_match.group(1)
    as_file = bool(event.pattern_match.group(2))

    session = ClientSession()

    async with session.get(NEKO_URL + nekotype) as response:
        if response.status == 200:
            image_url = (await response.json())["url"]
            await session.close()
        else:
            await event.reply(f"`An error occurred, response code: `**{response.status}**")
            await session.close()
            return

    try:
        await event.reply(file=image_url, force_document=as_file)
    except:
        await event.reply(f"`Failed to fetch media for query: `**{nekotype}**")
