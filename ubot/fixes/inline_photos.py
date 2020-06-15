import hashlib

from telethon import Button, utils
from telethon.tl import functions, types


async def photo(client, file, text='', parse_mode=None, buttons=None):
    try:
        fh = utils.get_input_photo(file)
    except TypeError:
        _, media, _ = await client._file_to_media(file, allow_cache=True, as_image=True)

        if isinstance(media, types.InputPhoto):
            fh = media
        else:
            r = await client(functions.messages.UploadMediaRequest(types.InputPeerSelf(), media=media))
            fh = utils.get_input_photo(r.photo)

    markup = None
    msg_entities = None

    if buttons:
        markup = client.build_reply_markup(buttons, inline_only=True)

    if text:
        text, msg_entities = await client._parse_message_text(text, parse_mode or client.parse_mode)

    result = types.InputBotInlineResultPhoto(
        id='',
        type='photo',
        photo=fh,
        send_message=types.InputBotInlineMessageMediaAuto(text, entities=msg_entities, reply_markup=markup)
    )

    result.id = hashlib.sha256(bytes(result)).hexdigest()

    return result
