from random import choice, shuffle

from ubot import ldr

BOARD_URL = "https://a.4cdn.org/{0}/threads.json"
POST_URL = "https://a.4cdn.org/{0}/thread/{1}.json"
CONTENT_URL = "https://i.4cdn.org/{0}/{1}{2}"
VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")
NSFW_BOARDS = ['aco', 'b', 'bant', 'd', 'e', 'f', 'gif', 'h', 'hc', 'hm', 'hr', 'i', 'ic', 'pol', 'r', 'r9k', 's', 's4s', 'soc', 't', 'trash', 'u', 'wg', 'y']


@ldr.add("4c", pattern_extra="(f|)", userlocking=True, pass_nsfw=True, help="Fetches images from 4chan, requires a board name as an argument.")
async def fourchan(event):
    if not event.args:
        await event.reply(f"Syntax: {ldr.prefix()}4c(f|) <board name>")
        return

    board = event.args.lower()
    as_file = bool(event.other_args[0])

    if event.nsfw_disabled and board in NSFW_BOARDS:
        await event.reply("Sorry, that board is NSFW and NSFW commands are disabled!")
        return

    async with ldr.aioclient.get(BOARD_URL.format(board)) as response:
        if response.status == 200:
            board_response = await response.json()
            op_id = choice(choice(board_response)["threads"])["no"]
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    async with ldr.aioclient.get(POST_URL.format(board, op_id)) as response:
        if response.status == 200:
            post_response = await response.json()
            post_info_list = [[i["tim"], i["ext"], i["com"] if "com" in i else None] for i in post_response["posts"] if "tim" in i and i["ext"] in VALID_ENDS]

            if not post_info_list:
                await event.reply(f"No results for board: **{board}**")
                return

            post_info = choice(post_info_list)
            post_file_url = CONTENT_URL.format(board, post_info[0], post_info[1])
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    if not response:
        await event.reply(f"No results for board: **{board}**")
        return

    try:
        await event.reply(post_info[2].replace("<br>", "\n") if post_info[2] else None, file=post_file_url, force_document=as_file, parse_mode="html")
        return
    except:
        pass

    await event.reply(f"Failed to fetch media for board: **{board}**")


@ldr.add_inline_photo("4c", default="4c")
async def fourchan_inline(event):
    if not event.args:
        return

    board = event.args.lower()

    async with ldr.aioclient.get(BOARD_URL.format(board)) as response:
        if response.status == 200:
            board_response = await response.json()
            op_id = choice(choice(board_response)["threads"])["no"]
        else:
            return

    post_file_url_list = []

    async with ldr.aioclient.get(POST_URL.format(board, op_id)) as response:
        if response.status == 200:
            post_response = await response.json()
            post_info_list = [[i["tim"], i["ext"], i["com"] if "com" in i else None] for i in post_response["posts"] if "tim" in i and i["ext"] in VALID_ENDS]

            if not post_info_list:
                return

            shuffle(post_info_list)

            for post_info in post_info_list[:3]:
                post_file_url_list += [CONTENT_URL.format(board, post_info[0], post_info[1])]
        else:
            return

    if not response:
        return

    return post_file_url_list
