# SPDX-License-Identifier: GPL-2.0-or-later

from random import choice

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

GEL_URL = "https://gelbooru.com/index.php"


@ldr.add("gel(s|x|q|)(f|)")
async def gelbooru(event):
    safety_arg = event.pattern_match.group(1)
    as_file = bool(event.pattern_match.group(2))
    rating = ""

    if safety_arg == "x":
        rating = "Rating:explicit"
    elif safety_arg == "s":
        rating = "Rating:safe"
    elif safety_arg == "q":
        rating = "Rating:questionable"

    params = {"page": "dapi",
              "s": "post",
              "q": "index",
              "json": 1,
              "tags": f"{rating} {event.args} sort:random".strip().replace("  ", " ")}

    async with ldr.aioclient.get(GEL_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.reply(f"`An error occurred, response code: `**{response.status}**")
            return

    if not response:
        await event.reply(f"`No results for query: `**{event.args}**")
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append(post['file_url'])

    if not valid_urls:
        await event.reply(f"`Failed to find URLs for query: `**{event.args}**")
        return

    for image_url in valid_urls:
        try:
            await event.reply(file=image_url, force_document=as_file)
            return
        except:
            pass

    await event.reply(f"`Failed to fetch media for query: `**{event.args}**")
