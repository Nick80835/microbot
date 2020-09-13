# SPDX-License-Identifier: GPL-2.0-or-later

from ubot import ldr

YAN_URL = "https://yande.re/post.json"
YAN_SAUCE_URL = "https://yande.re/post/show/"


@ldr.add_list(["yan", "yanx", "yanq", "yans"], pattern_extra="(f|)", help="Fetches images from Yande.re, takes tags as arguments.")
async def yandere(event):
    await event.edit(f"`Processing…`")
    safety_arg = event.command[-1]
    as_file = bool(event.other_args[0])
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

    async with ldr.aioclient.get(YAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    if not response:
        await event.edit(f"`No results for query: `**{event.args}**")
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append([post['file_url'], post['id']])

    if not valid_urls:
        await event.edit(f"`Failed to find URLs for query: `**{event.args}**")
        return

    for image in valid_urls:
        try:
            await event.client.send_message(event.chat_id, f"[sauce]({YAN_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            await event.delete()
            return
        except:
            pass

    await event.edit(f"`Failed to fetch media for query: `**{event.args}**")
