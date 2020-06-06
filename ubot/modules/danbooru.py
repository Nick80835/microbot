# SPDX-License-Identifier: GPL-2.0-or-later

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

DAN_URL = "http://danbooru.donmai.us/posts.json"
DAN_SAUCE_URL = "https://danbooru.donmai.us/posts/"


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

    async with ldr.aioclient.get(DAN_URL, params=params) as response:
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
            await event.reply(f"[sauce]({DAN_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("dan(s|x|q|)", default="dan")
async def danbooru_inline(event):
    safety_arg = event.pattern_match.group(1)
    rating = ""

    if safety_arg == "x":
        rating = "Rating:explicit"
    elif safety_arg == "s":
        rating = "Rating:safe"
    elif safety_arg == "q":
        rating = "Rating:questionable"

    params = {"limit": 3,
              "random": "true",
              "tags": f"{rating} {event.args}".strip().replace("  ", " ")}

    async with ldr.aioclient.get(DAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            return None

    if not response:
        return None

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append(post['file_url'])

    if not valid_urls:
        return None

    return valid_urls[:3]
