# SPDX-License-Identifier: GPL-2.0-or-later

from time import time_ns

from telethon import Button

from ubot import ldr

KON_URL = "https://konachan.com/post.json"
KON_SAUCE_URL = "https://konachan.com/post/show/"
kon_button_dict = {}
help_string = "Fetches images from Konachan, takes tags as arguments."


@ldr.add("konping", sudo=True, hide_help=True)
async def konachan_ping(event):
    params = {"limit": 1,
              "tags": "order:random"}

    start = time_ns()

    async with ldr.aioclient.get(KON_URL, params=params) as _:
        time_taken_ms = int((time_ns() - start) / 1000000)
        await event.reply(f"Konachan response time -> **{time_taken_ms}**ms")


@ldr.add_list(["kon", "konx", "konq"], pattern_extra="(f|)", nsfw=True, userlocking=True, help=help_string)
@ldr.add("kons", pattern_extra="(f|)", userlocking=True, help=help_string)
async def konachan(event):
    safety_arg = event.command[-1]
    as_file = bool(event.other_args[0])
    rating = ""

    if safety_arg == "x":
        rating = "rating:x"
    elif safety_arg == "s":
        rating = "rating:s"
    elif safety_arg == "q":
        rating = "rating:q"

    params = {"limit": 3,
              "tags": f"order:random {rating} {event.args}".strip().replace("  ", " ")}

    async with ldr.aioclient.get(KON_URL, params=params) as response:
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
            await event.reply(f"[sauce]({KON_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("kon(s|x|q|)", default="kon")
async def konachan_inline(event):
    safety_arg = event.other_args[0]
    rating = ""

    if safety_arg == "x":
        rating = "rating:x"
    elif safety_arg == "s":
        rating = "rating:s"
    elif safety_arg == "q":
        rating = "rating:q"

    params = {"limit": 3,
              "tags": f"order:random {rating} {event.args}".strip().replace("  ", " ")}

    async with ldr.aioclient.get(KON_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            return

    if not response:
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append([post['file_url'], f"[sauce]({KON_SAUCE_URL}{post['id']})"])

    if not valid_urls:
        return

    return valid_urls[:3]


@ldr.add("konb", nsfw=True, userlocking=True)
async def konachan_buttons(event):
    params = {"limit": 30,
              "tags": f"order:random {event.args}".strip()}

    async with ldr.aioclient.get(KON_URL, params=params) as response:
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

    kon_button_dict[f"{event.chat.id}_{event.id}"] = [0, valid_urls]

    await event.reply(
        f"[sauce]({KON_SAUCE_URL}{valid_urls[0][1]})",
        file=valid_urls[0][0],
        buttons=[Button.inline('➡️', f'kon*{event.chat.id}_{event.id}*r')]
    )


@ldr.add_callback_query("kon")
async def konachan_buttons_callback(event):
    args_split = event.args.split("*")

    dict_id = args_split[0]
    direction = args_split[1]

    if dict_id in kon_button_dict:
        this_dict = kon_button_dict[dict_id]
    else:
        return

    if direction == "r":
        this_dict[0] += 1

        if this_dict[0] + 1 > len(this_dict[1]):
            this_dict[0] = len(this_dict[1]) - 1

        this_image = this_dict[1][this_dict[0]]
    elif direction == "l":
        this_dict[0] -= 1

        if this_dict[0] < 0:
            this_dict[0] = 0

        this_image = this_dict[1][this_dict[0]]

    buttons = []

    if this_dict[0] > 0:
        buttons += [Button.inline('⬅️', f'kon*{dict_id}*l')]

    if len(this_dict[1]) - 1 > this_dict[0]:
        buttons += [Button.inline('➡️', f'kon*{dict_id}*r')]

    try:
        await event.edit(
            f"[sauce]({KON_SAUCE_URL}{this_image[1]})",
            file=this_image[0],
            buttons=buttons
        )
    except:
        pass
