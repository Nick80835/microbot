# SPDX-License-Identifier: GPL-2.0-or-later

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

SAN_URL = "https://capi-v2.sankakucomplex.com/posts"


@ldr.add("san(s|x|q|)(f|)")
async def sankaku(event):
    await event.edit(f"`Processing…`")
    safety_arg = event.pattern_match.group(1)
    as_file = bool(event.pattern_match.group(2))
    rating = ""

    if safety_arg == "x":
        rating = "rating:explicit"
    elif safety_arg == "s":
        rating = "rating:safe"
    elif safety_arg == "q":
        rating = "rating:questionable"

    params = {"page": 1,
              "limit": 5,
              "tags": f"order:random {rating} {event.args}".strip().replace("  ", " ")}

    session = ClientSession()

    async with session.get(SAN_URL, params=params) as response:
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

    for item in response:
        if 'file_url' in item.keys():
            valid_urls.append(item['file_url'])

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
