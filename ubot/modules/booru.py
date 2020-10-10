# SPDX-License-Identifier: GPL-2.0-or-later

from asyncbooru import Danbooru, Gelbooru, Konachan, Sankaku, Yandere
from ubot import ldr

commands = {
    ("dan", "danx", "danq", "dans"): Danbooru(ldr.aioclient),
    ("gel", "gelx", "gelq", "gels"): Gelbooru(ldr.aioclient),
    ("kon", "konx", "konq", "kons"): Konachan(ldr.aioclient),
    ("san", "sanx", "sanq", "sans"): Sankaku(ldr.aioclient),
    ("yan", "yanx", "yanq", "yans"): Yandere(ldr.aioclient)
}


@ldr.add_dict(commands, pattern_extra="(f|)", help="Fetches images from Danbooru, Gelbooru, Konachan, Sankaku Complex and Yandere, takes tags as arguments.")
async def booru(event):
    await event.edit(f"`Processing…`")
    safety_arg = event.command[-1]
    as_file = bool(event.other_args[0])
    post = await event.extra.get_random_post(event.args, safety_arg)

    if not post or not post.file_url:
        await event.edit(f"`No results for query: `**{event.args}**")
        return

    try:
        await event.respond(f"[sauce]({post.sauce})", file=post.file_url, force_document=as_file)
        await event.delete()
    except:
        await event.edit(f"`Failed to fetch media for query: `**{event.args}**")
