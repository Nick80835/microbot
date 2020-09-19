# SPDX-License-Identifier: GPL-2.0-or-later

from time import time_ns

from telethon import Button

from ubot import ldr

SAN_URL = "https://capi-v2.sankakucomplex.com/posts"
SAN_SAUCE_URL = "https://beta.sankakucomplex.com/post/show/"
help_string = "Fetches images from Sankaku Complex, takes tags as arguments."


@ldr.add("sanping", sudo=True, hide_help=True)
async def sankaku_ping(event):
    params = {"page": 1,
              "limit": 3,
              "tags": f"order:random"}

    start = time_ns()

    async with ldr.aioclient.get(SAN_URL, params=params) as _:
        time_taken_ms = int((time_ns() - start) / 1000000)
        await event.reply(f"Sankaku response time -> **{time_taken_ms}**ms")


@ldr.add_list(["san", "sanx", "sanq"], pattern_extra="(f|)", nsfw=True, userlocking=True, help=help_string)
@ldr.add("sans", pattern_extra="(f|)", userlocking=True, help=help_string)
async def sankaku(event):
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

    async with ldr.aioclient.get(SAN_URL, params=params) as response:
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
            await event.reply(f"[sauce]({SAN_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("san(s|x|q|)", default="san")
async def sankaku_inline(event):
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

    async with ldr.aioclient.get(SAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            return

    if not response:
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append([post['file_url'], f"[sauce]({SAN_SAUCE_URL}{post['id']})"])

    if not valid_urls:
        return

    return valid_urls[:3]


@ldr.add("sanb", nsfw=True, userlocking=True)
async def sankaku_buttons(event):
    params = {"page": 1,
              "limit": 30,
              "tags": f"order:random {event.args}".strip()}

    async with ldr.aioclient.get(SAN_URL, params=params) as response:
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

    ldr.get_cbs_by_func(sankaku_buttons_callback)[0].data[f"{event.chat.id}_{event.id}"] = [0, valid_urls]

    await event.reply(
        f"[sauce]({SAN_SAUCE_URL}{valid_urls[0][1]})",
        file=valid_urls[0][0],
        buttons=[Button.inline('➡️', f'san*{event.chat.id}_{event.id}*r')]
    )


@ldr.add_callback_query("san")
async def sankaku_buttons_callback(event):
    args_split = event.args.split("*")

    dict_id = args_split[0]
    direction = args_split[1]

    if dict_id in event.object.data:
        this_dict = event.object.data[dict_id]
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
        buttons += [Button.inline('⬅️', f'san*{dict_id}*l')]

    if len(this_dict[1]) - 1 > this_dict[0]:
        buttons += [Button.inline('➡️', f'san*{dict_id}*r')]

    try:
        await event.edit(
            f"[sauce]({SAN_SAUCE_URL}{this_image[1]})",
            file=this_image[0],
            buttons=buttons
        )
    except:
        pass
