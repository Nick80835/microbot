# SPDX-License-Identifier: GPL-2.0-or-later

from random import choice
from time import time_ns

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

GEL_URL = "https://gelbooru.com/index.php"
GEL_SAUCE_URL = "https://gelbooru.com/index.php?page=post&s=view&id="


@ldr.add("gelping", sudo=True, hide_help=True)
async def danbooru_ping(event):
    params = {"page": "dapi",
              "s": "post",
              "q": "index",
              "json": 1,
              "tags": f"sort:random"}

    start = time_ns()

    async with ldr.aioclient.get(GEL_URL, params=params) as _:
        time_taken_ms = int((time_ns() - start) / 1000000)
        await event.reply(f"Gelbooru response time -> **{time_taken_ms}**ms")


@ldr.add("gel(s|x|q|)(f|)", nsfw=True, userlocking=True)
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
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    if not response:
        await event.reply(f"No results for query: {event.args}")
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append([post['file_url'], post['id']])

    if not valid_urls:
        await event.reply(f"Failed to find URLs for query: {event.args}")
        return

    for image in valid_urls:
        try:
            await event.reply(f"[sauce]({GEL_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("gel(s|x|q|)", default="gel")
async def gelbooru_inline(event):
    safety_arg = event.pattern_match.group(1)
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
            return None

    if not response:
        return None

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append([post['file_url'], f"[sauce]({GEL_SAUCE_URL}{post['id']})"])

    if not valid_urls:
        return None

    return valid_urls[:3]
