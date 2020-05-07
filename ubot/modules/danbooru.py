# SPDX-License-Identifier: GPL-2.0-or-later

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

DAN_URL = "http://danbooru.donmai.us/posts.json"


@ldr.add("dan(s|x|q|)(f|)")
async def danbooru(event):
    await event.edit(f"`Processing…`")
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
            await session.close()
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            await session.close()
            return

    if not response:
        await event.edit(f"`No results for query: `**{event.args}**")
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append(post['file_url'])

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
