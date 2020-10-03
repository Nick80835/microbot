# SPDX-License-Identifier: GPL-2.0-or-later

from asyncbooru import Konachan
from ubot import ldr

konachan_api = Konachan(ldr.aioclient)


@ldr.add_list(["kon", "konx", "konq", "kons"], pattern_extra="(f|)", help="Fetches images from Konachan, takes tags as arguments.")
async def konachan(event):
    await event.edit(f"`Processing…`")
    safety_arg = event.command[-1]
    as_file = bool(event.other_args[0])
    post = await konachan_api.get_random_post(event.args, safety_arg)

    if not post or not post.file_url:
        await event.edit(f"`No results for query: `**{event.args}**")
        return

    try:
        await event.client.send_message(event.chat_id, f"[sauce]({post.sauce})", file=post.file_url, force_document=as_file)
        await event.delete()
    except:
        await event.edit(f"`Failed to fetch media for query: `**{event.args}**")
