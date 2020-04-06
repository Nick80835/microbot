# SPDX-License-Identifier: GPL-2.0-or-later

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

DAN_URL = "http://danbooru.donmai.us/posts.json"


@ldr.add(pattern="dan(s|x|q|)(f|)")
async def danbooru(event):
    if "x" in event.pattern_match.group(0):
        rating = "Rating:explicit"
    elif "s" in event.pattern_match.group(0):
        rating = "Rating:safe"
    elif "q" in event.pattern_match.group(0):
        rating = "Rating:questionable"
    else:
        rating = ""

    if event.pattern_match.group(2):
        as_file = True
    else:
        as_file = False

    search_query = event.pattern_match.group(3)

    params = {"limit": 1,
              "random": "true",
              "tags": f"{rating} {search_query}".strip()}

    session = ClientSession()

    async with session.get(DAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.reply(f"`An error occurred, response code: `**{response.status}**")
            await session.close()
            return

    await session.close()

    if not response:
        await event.reply(f"`No results for query: `**{search_query}**")
        return

    valid_urls = []

    for url in ['file_url', 'large_file_url', 'source']:
        if url in response[0].keys():
            valid_urls.append(response[0][url])

    if not valid_urls:
        await event.reply(f"`Failed to find URLs for query: `**{search_query}**")
        return

    for image_url in valid_urls:
        try:
            await event.reply(file=image_url, force_document=as_file)
            return
        except:
            pass

    await event.reply(f"`Failed to fetch media for query: `**{search_query}**")
