# SPDX-License-Identifier: GPL-2.0-or-later

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

DAN_URL = "http://danbooru.donmai.us/posts.json"


@ldr.add("dan(s|x|q|)(f|)")
async def danbooru(event):
    safety_arg = event.pattern_match.group(1)
    as_file = bool(event.pattern_match.group(2))
    rating = ""

    if safety_arg == "x":
        rating = "Rating:explicit"
    elif safety_arg == "s":
        rating = "Rating:safe"
    elif safety_arg == "q":
        rating = "Rating:questionable"

    params = {"limit": 1,
              "random": "true",
              "tags": f"{rating} {event.args}".strip().replace("  ", " ")}

    session = ClientSession()

    async with session.get(DAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            await session.close()
            return

    await session.close()

    if not response:
        await event.edit(f"`No results for query: `**{event.args}**")
        return

    valid_urls = []

    for url in ['file_url', 'large_file_url', 'source']:
        if url in response[0].keys():
            valid_urls.append(response[0][url])

    if not valid_urls:
        await event.edit(f"`Failed to find URLs for query: `**{event.args}**")
        return

    for image_url in valid_urls:
        try:
            await event.client.send_file(event.chat_id, file=image_url, force_document=as_file)
            await event.delete()
            return
        except:
            pass

    await event.edit(f"`Failed to fetch media for query: `**{event.args}**")
