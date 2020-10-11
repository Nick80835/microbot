# SPDX-License-Identifier: GPL-2.0-or-later

import io

from ubot import ldr

UD_QUERY_URL = 'http://api.urbandictionary.com/v0/define'
UD_RANDOM_URL = 'http://api.urbandictionary.com/v0/random'


@ldr.add("ud", help="Fetches words from Urban Dictionary, takes an optional word as an argument.")
async def urban_dict(event):
    udquery = event.args

    if udquery:
        params = {'term': udquery}
        url = UD_QUERY_URL
    else:
        params = None
        url = UD_RANDOM_URL

    async with ldr.aioclient.get(url, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.reply(f"An error occurred, response code: **{response.status}**")
            return

    if response['list']:
        response_word = response['list'][0]
    else:
        await event.reply(f"No results for query: **{udquery}**")
        return

    definition = f"**{response_word['word']}**: {response_word['definition']}"

    if response_word['example']:
        definition += f"\n\n**Example**: {response_word['example']}"

    definition = definition.replace("[", "").replace("]", "")

    if len(definition) >= 4096:
        file_io = io.BytesIO()
        file_io.write(bytes(definition.encode('utf-8')))
        file_io.name = f"definition of {response_word['word']}.txt"
        await event.reply("Output was too large, sent it as a file.", file=file_io)
        return

    await event.reply(definition)


@ldr.add_inline_article("ud", default="ud")
async def urban_dict_inline(event):
    udquery = event.args

    if udquery:
        params = {'term': udquery}
        url = UD_QUERY_URL
    else:
        params = None
        url = UD_RANDOM_URL

    async with ldr.aioclient.get(url, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            return

    if response['list']:
        response_words = response['list'][:10]
    else:
        return

    definition_list = []

    for word in response_words:
        word['definition'] = word['definition'].replace("[", "").replace("]", "")
        definition = {"title": word['word'], "description": word['definition'], "text": f"**{word['word']}**: {word['definition']}"}

        if word['example']:
            definition['text'] += f"\n\n**Example**: {word['example']}".replace("[", "").replace("]", "")

        definition_list += [definition]

    return definition_list
