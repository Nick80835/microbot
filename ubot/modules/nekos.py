import io
import random

from PIL import Image

from ubot import ldr

NEKO_URL = "https://nekos.life/api/v2/img/"
ES_NEKO_TYPES = ['tetas', 'acariciar', 'abrazar', 'abofetear', 'nalguear', 'pies', 'mamada', 'coño', 'concha',
                 'besar', 'presumir', 'cosquillas']
NEKO_TYPES = ['neko', 'lewd', 'smug', 'tits', 'trap', 'anal', 'cuddle', 'hug', 'slap', 'spank', 'pat', 'kuni', 'femdom',
              'feet', 'baka', 'blowjob', 'Random_hentai_gif', 'erok', 'feetg', 'bj', 'erokemo', 'tickle', 'feed',
              'futanari', 'poke', 'les', 'boobs', 'hentai', 'hololewd', 'ngif', 'fox_girl', 'wallpaper',
              'lewdk', 'solog', 'pussy', 'yuri', 'lewdkemo', 'pwankg', 'eron', 'kiss', 'keta', 'eroyuri', 'cum_jpg',
              'gecg', 'holoero', 'classic', 'kemonomimi', 'erofeet', 'ero', 'solo', 'cum', 'holo',
              'nsfw_neko_gif']
REPLY_TYPES = ['cuddle', 'hug', 'slap', 'spank', 'pat', 'baka', 'blowjob', 'kiss', 'pussy_jpg', 'tickle', 'poke']


def spanishify(es_text):
    """
    Translate spanish commands to english
    :param es_text:
    :return:
    """
    if es_text == 'tetas':
        return 'boobs'
    elif es_text == 'acariciar':
        return random.choice(['cuddle', 'pat'])
    elif es_text == 'abrazar':
        return 'hug'
    elif es_text == 'abofetear':
        return 'slap'
    elif es_text == 'nalguear':
        return 'spank'
    elif es_text == 'pies':
        return 'feet'
    elif es_text == 'mamada':
        return random.choice(['blowjob', 'bj'])
    elif es_text in ['coño', 'concha']:
        return 'pussy'
    elif es_text == 'besar':
        return 'kiss'
    elif es_text == 'presumir':
        return 'smug'
    elif es_text == 'cosquillas':
        return 'tickle'
    else:
        return es_text


@ldr.add_list(NEKO_TYPES + ES_NEKO_TYPES, pattern_extra="(f|)")
async def supernekoatsume(event):
    await event.edit("`Processing…`")
    nekotype = event.command.lower()
    as_file = bool(event.other_args[0])

    if nekotype == 'random_hentai_gif':
        nekotype = 'Random_hentai_gif'

    nekotype = spanishify(nekotype)

    if nekotype in REPLY_TYPES:
        reply_to = await event.get_reply_message()
    else:
        reply_to = None

    async with ldr.aioclient.get(NEKO_URL + nekotype) as response:
        if response.status == 200:
            image_url = (await response.json())["url"]
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    try:
        await event.respond(file=image_url, force_document=as_file, reply_to=reply_to)
        await event.delete()
    except:
        await event.edit(f"`Failed to fetch media for query: `**{nekotype}**")


@ldr.add("8ball")
async def eightball(event):
    await event.edit("`Processing…`")

    async with ldr.aioclient.get(NEKO_URL + "8ball") as response:
        if response.status == 200:
            image_url = (await response.json())["url"]
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    async with ldr.aioclient.get(image_url) as response:
        if response.status == 200:
            image_data = await response.read()
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    try:
        await event.respond(file=await ldr.run_async(eightballsync, image_data))
        await event.delete()
    except:
        await event.edit("`Failed to send 8ball! :(`")


def eightballsync(image_data):
    sticker_image = Image.open(io.BytesIO(image_data))
    sticker_image = sticker_image.resize((512, 512), Image.BILINEAR)
    sticker_io = io.BytesIO()
    sticker_image.save(sticker_io, "WebP", quality=99)
    sticker_io.seek(0)
    sticker_io.name = "sticker.webp"

    return sticker_io
