# SPDX-License-Identifier: GPL-2.0-or-later

from time import time_ns

from telethon import Button

from ubot import ldr

YAN_URL = "https://yande.re/post.json"
YAN_SAUCE_URL = "https://yande.re/post/show/"
yan_button_dict = {}
help_string = "Fetches images from Yande.re, takes tags as arguments."


@ldr.add("yanping", sudo=True, hide_help=True)
async def yandere_ping(event):
    params = {"page": 1,
              "limit": 3,
              "tags": f"order:random"}

    start = time_ns()

    async with ldr.aioclient.get(YAN_URL, params=params) as _:
        time_taken_ms = int((time_ns() - start) / 1000000)
        await event.reply(f"Yande.re response time -> **{time_taken_ms}**ms")


@ldr.add_list(["yan", "yanx", "yanq"], pattern_extra="(f|)", nsfw=True, userlocking=True, help=help_string)
@ldr.add("yans", pattern_extra="(f|)", userlocking=True, help=help_string)
async def yandere(event):
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
              "limit": 3,
              "tags": f"order:random {rating} {event.args}".strip().replace("  ", " ")}

    async with ldr.aioclient.get(YAN_URL, params=params) as response:
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
            await event.reply(f"[sauce]({YAN_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("yan(s|x|q|)", default="yan")
async def yandere_inline(event):
    safety_arg = event.other_args[0]
    rating = ""

    if safety_arg == "x":
        rating = "rating:explicit"
    elif safety_arg == "s":
        rating = "rating:safe"
    elif safety_arg == "q":
        rating = "rating:questionable"

    params = {"page": 1,
              "limit": 3,
              "tags": f"order:random {rating} {event.args}".strip().replace("  ", " ")}

    async with ldr.aioclient.get(YAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            return

    if not response:
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append([post['file_url'], f"[sauce]({YAN_SAUCE_URL}{post['id']})"])

    if not valid_urls:
        return

    return valid_urls[:3]


@ldr.add("yanb", nsfw=True, userlocking=True)
async def yandere_buttons(event):
    params = {"page": 1,
              "limit": 30,
              "tags": f"order:random {event.args}".strip()}

    async with ldr.aioclient.get(YAN_URL, params=params) as response:
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

    yan_button_dict[f"{event.chat.id}_{event.id}"] = [0, valid_urls]

    await event.reply(
        f"[sauce]({YAN_SAUCE_URL}{valid_urls[0][1]})",
        file=valid_urls[0][0],
        buttons=[Button.inline('➡️', f'yan*{event.chat.id}_{event.id}*r')]
    )


@ldr.add_callback_query("yan")
async def yandere_buttons_callback(event):
    args_split = event.args.split("*")

    dict_id = args_split[0]
    direction = args_split[1]

    if dict_id in yan_button_dict:
        this_dict = yan_button_dict[dict_id]
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
        buttons += [Button.inline('⬅️', f'yan*{dict_id}*l')]

    if len(this_dict[1]) - 1 > this_dict[0]:
        buttons += [Button.inline('➡️', f'yan*{dict_id}*r')]

    try:
        await event.edit(
            f"[sauce]({YAN_SAUCE_URL}{this_image[1]})",
            file=this_image[0],
            buttons=buttons
        )
    except:
        pass
