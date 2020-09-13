# SPDX-License-Identifier: GPL-2.0-or-later

from random import choice

from ubot import ldr

BOARD_URL = "https://a.4cdn.org/{0}/threads.json"
POST_URL = "https://a.4cdn.org/{0}/thread/{1}.json"
CONTENT_URL = "https://i.4cdn.org/{0}/{1}{2}"
VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


@ldr.add("4c", pattern_extra="(f|)", help="Fetches images from 4chan, requires a board name as an argument.")
async def fourchan(event):
    if not event.args:
        await event.edit(f"`Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}4c(f|) <board name>`")
        return

    await event.edit(f"`Processing…`")
    as_file = bool(event.other_args[0])

    async with ldr.aioclient.get(BOARD_URL.format(event.args)) as response:
        if response.status == 200:
            board_response = await response.json()
            op_id = choice(choice(board_response)["threads"])["no"]
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    async with ldr.aioclient.get(POST_URL.format(event.args, op_id)) as response:
        if response.status == 200:
            post_response = await response.json()
            post_info = choice([[i["tim"], i["ext"], i["com"] if "com" in i else None] for i in post_response["posts"] if "tim" in i and i["ext"] in VALID_ENDS])
            post_file_url = CONTENT_URL.format(event.args, post_info[0], post_info[1])
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    if not response:
        await event.edit(f"`No results for board: `**{event.args}**")
        return

    try:
        await event.client.send_file(event.chat_id, file=post_file_url, force_document=as_file, caption=post_info[2].replace("<br>", "\n") if post_info[2] else None, parse_mode="html")
        await event.delete()
        return
    except:
        pass

    await event.edit(f"`Failed to fetch media for board: `**{event.args}**")
