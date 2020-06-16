# SPDX-License-Identifier: GPL-2.0-or-later

from random import choice, shuffle

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

BOARD_URL = "https://a.4cdn.org/{0}/threads.json"
POST_URL = "https://a.4cdn.org/{0}/thread/{1}.json"
CONTENT_URL = "https://i.4cdn.org/{0}/{1}{2}"
VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


@ldr.add("4c(f|)", userlocking=True)
async def fourchan(event):
    if not event.args:
        await event.reply(f"Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}4c(f|) <board name>")
        return

    as_file = bool(event.pattern_match.group(1))

    async with ldr.aioclient.get(BOARD_URL.format(event.args)) as response:
        if response.status == 200:
            board_response = await response.json()
            op_id = choice(choice(board_response)["threads"])["no"]
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    async with ldr.aioclient.get(POST_URL.format(event.args, op_id)) as response:
        if response.status == 200:
            post_response = await response.json()
            post_info = choice([[i["tim"], i["ext"], i["com"] if "com" in i else None] for i in post_response["posts"] if "tim" in i and i["ext"] in VALID_ENDS])
            post_file_url = CONTENT_URL.format(event.args, post_info[0], post_info[1])
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    if not response:
        await event.reply(f"No results for board: **{event.args}**")
        return

    try:
        await event.reply(post_info[2].replace("<br>", "\n") if post_info[2] else None, file=post_file_url, force_document=as_file, parse_mode="html")
        return
    except:
        pass

    await event.reply(f"Failed to fetch media for board: **{event.args}**")


@ldr.add_inline_photo("4c", default="4c")
async def fourchan_inline(event):
    if not event.args:
        return None

    async with ldr.aioclient.get(BOARD_URL.format(event.args)) as response:
        if response.status == 200:
            board_response = await response.json()
            op_id = choice(choice(board_response)["threads"])["no"]
        else:
            return None

    post_file_url_list = []

    async with ldr.aioclient.get(POST_URL.format(event.args, op_id)) as response:
        if response.status == 200:
            post_response = await response.json()
            post_info_list = [[i["tim"], i["ext"], i["com"] if "com" in i else None] for i in post_response["posts"] if "tim" in i and i["ext"] in VALID_ENDS]
            shuffle(post_info_list)

            for post_info in post_info_list[:3]:
                post_file_url_list += [CONTENT_URL.format(event.args, post_info[0], post_info[1])]
        else:
            return None

    if not response:
        return None

    return post_file_url_list
