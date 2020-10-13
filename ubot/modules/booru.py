from asyncbooru import Danbooru, Gelbooru, Konachan, Sankaku, Yandere
from telethon import Button
from ubot import ldr

help_str = "Fetches images from Danbooru, Gelbooru, Konachan, Sankaku Complex and Yandere, takes tags as arguments."

dan_api = Danbooru(ldr.aioclient)
gel_api = Gelbooru(ldr.aioclient)
kon_api = Konachan(ldr.aioclient)
san_api = Sankaku(ldr.aioclient)
yan_api = Yandere(ldr.aioclient)

dan_butt = {}
gel_butt = {}
kon_butt = {}
san_butt = {}
yan_butt = {}

commands_sfw = {
    "dans": dan_api,
    "gels": gel_api,
    "kons": kon_api,
    "sans": san_api,
    "yans": yan_api
}

commands_nsfw = {
    ("dan", "danx", "danq"): dan_api,
    ("gel", "gelx", "gelq"): gel_api,
    ("kon", "konx", "konq"): kon_api,
    ("san", "sanx", "sanq"): san_api,
    ("yan", "yanx", "yanq"): yan_api
}

commands_butt = {
    "danb": [dan_api, dan_butt, "dan"],
    "gelb": [gel_api, gel_butt, "gel"],
    "konb": [kon_api, kon_butt, "kon"],
    "sanb": [san_api, san_butt, "san"],
    "yanb": [yan_api, yan_butt, "yan"]
}


@ldr.add_dict(commands_sfw, pattern_extra="(f|)", help=help_str, userlocking=True)
@ldr.add_dict(commands_nsfw, pattern_extra="(f|)", help=help_str, userlocking=True, nsfw=True)
async def booru(event):
    safety_arg = event.command[-1]
    as_file = bool(event.other_args[0])
    posts = await event.extra.get_random_posts(event.args, 3, safety_arg)

    if not posts:
        await event.reply(f"No results for query: {event.args}")
        return

    images = [[post.file_url, post.sauce] for post in posts if post.file_url]

    if not images:
        await event.reply(f"Failed to find URLs for query: {event.args}")
        return

    for image in images:
        try:
            await event.reply(f"[sauce]({image[1]})", file=image[0], force_document=as_file)
            return
        except:
            pass

    await event.reply(f"Failed to fetch media for query: {event.args}")


@ldr.add_inline_photo("dan(s|x|q|)", default="dan", extra=dan_api)
@ldr.add_inline_photo("gel(s|x|q|)", default="gel", extra=gel_api)
@ldr.add_inline_photo("kon(s|x|q|)", default="kon", extra=kon_api)
@ldr.add_inline_photo("san(s|x|q|)", default="san", extra=san_api)
@ldr.add_inline_photo("yan(s|x|q|)", default="yan", extra=yan_api)
async def booru_inline(event):
    posts = await event.extra.get_random_posts(event.args, 3, event.other_args[0])
    return [[post.file_url, f"[sauce]({post.sauce})"] for post in posts if post.file_url] if posts else None


@ldr.add_dict(commands_butt, help=help_str, userlocking=True, nsfw=True)
async def booru_buttons(event):
    posts = await event.extra[0].get_random_posts(event.args, 30)

    if not posts:
        await event.reply(f"No results for query: {event.args}")
        return

    images = [[post.file_url, post.sauce] for post in posts if post.file_url]

    if not images:
        await event.reply(f"Failed to find URLs for query: {event.args}")
        return

    event.extra[1][f"{event.chat.id}_{event.id}"] = [0, images]

    await event.reply(
        f"[sauce]({images[0][1]})",
        file=images[0][0],
        buttons=[Button.inline('➡️', f'{event.extra[2]}*{event.chat.id}_{event.id}*r')]
    )


@ldr.add_callback_query("dan", extra=dan_butt)
@ldr.add_callback_query("gel", extra=gel_butt)
@ldr.add_callback_query("kon", extra=kon_butt)
@ldr.add_callback_query("san", extra=san_butt)
@ldr.add_callback_query("yan", extra=yan_butt)
async def booru_buttons_callback(event):
    args_split = event.args.split("*")

    dict_id = args_split[0]
    direction = args_split[1]

    if dict_id in event.extra:
        this_dict = event.extra[dict_id]
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
        buttons += [Button.inline('⬅️', f'{event.command}*{dict_id}*l')]

    if len(this_dict[1]) - 1 > this_dict[0]:
        buttons += [Button.inline('➡️', f'{event.command}*{dict_id}*r')]

    try:
        await event.edit(
            f"[sauce]({this_image[1]})",
            file=this_image[0],
            buttons=buttons
        )
    except:
        pass
