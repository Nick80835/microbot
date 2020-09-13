# SPDX-License-Identifier: GPL-2.0-or-later

from ubot import ldr

DAN_URL = "http://danbooru.donmai.us/posts.json"
DAN_SAUCE_URL = "https://danbooru.donmai.us/posts/"


@ldr.add_list(["dan", "danx", "danq", "dans"], pattern_extra="(f|)", help="Fetches images from Danbooru, takes tags as arguments.")
async def danbooru(event):
    await event.edit(f"`Processing…`")
    safety_arg = event.command[-1]
    as_file = bool(event.other_args[0])
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
            await event.client.send_message(event.chat_id, f"[sauce]({DAN_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            await event.delete()
            return
        except:
            pass

    await event.edit(f"`Failed to fetch media for query: `**{event.args}**")
