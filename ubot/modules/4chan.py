# SPDX-License-Identifier: GPL-2.0-or-later

from random import choice

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

BOARD_URL = "https://a.4cdn.org/{0}/threads.json"
POST_URL = "https://a.4cdn.org/{0}/thread/{1}.json"
CONTENT_URL = "https://i.4cdn.org/{0}/{1}{2}"
VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


@ldr.add("4c(f|)")
async def fourchan(event):
    as_file = bool(event.pattern_match.group(1))

    session = ClientSession()

    async with session.get(BOARD_URL.format(event.args)) as response:
        if response.status == 200:
            board_response = await response.json()
            op_id = choice(choice(board_response)["threads"])["no"]
        else:
            await event.reply(f"`An error occurred, response code: `**{response.status}**")
            await session.close()
            return

    async with session.get(POST_URL.format(event.args, op_id)) as response:
        if response.status == 200:
            post_response = await response.json()
            post_info = choice([[i["tim"], i["ext"], i["com"] if "com" in i else None] for i in post_response["posts"] if "tim" in i and i["ext"] in VALID_ENDS])
            post_file_url = CONTENT_URL.format(event.args, post_info[0], post_info[1])
        else:
            await event.reply(f"`An error occurred, response code: `**{response.status}**")
            await session.close()
            return

    await session.close()

    if not response:
        await event.reply(f"`No results for board: `**{event.args}**")
        return

    try:
        await event.reply(post_info[2].replace("<br>", "\n") if post_info[2] else None, file=post_file_url, force_document=as_file, parse_mode="html")
        return
    except:
        pass

    await event.reply(f"`Failed to fetch media for board: `**{event.args}**")
