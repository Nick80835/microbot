# SPDX-License-Identifier: GPL-2.0-or-later

from ubot import ldr

GEL_URL = "https://gelbooru.com/index.php"
GEL_SAUCE_URL = "https://gelbooru.com/index.php?page=post&s=view&id="


@ldr.add_list(["gel", "gelx", "gelq", "gels"], pattern_extra="(f|)", help="Fetches images from Gelbooru, takes tags as arguments.")
async def gelbooru(event):
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

    params = {"page": "dapi",
              "s": "post",
              "q": "index",
              "json": 1,
              "tags": f"{rating} {event.args} sort:random".strip().replace("  ", " ")}

    async with ldr.aioclient.get(GEL_URL, params=params) as response:
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
            await event.client.send_message(event.chat_id, f"[sauce]({GEL_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            await event.delete()
            return
        except:
            pass

    await event.edit(f"`Failed to fetch media for query: `**{event.args}**")
