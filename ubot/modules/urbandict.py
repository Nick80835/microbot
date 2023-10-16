# SPDX-License-Identifier: GPL-2.0-or-later

import io

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

UD_QUERY_URL = 'http://api.urbandictionary.com/v0/define'
UD_RANDOM_URL = 'http://api.urbandictionary.com/v0/random'


@ldr.add(pattern="ud")
async def urban_dict(event):
    udquery = event.args

    if udquery:
        params = {'term': udquery}
        url = UD_QUERY_URL
    else:
        params = None
        url = UD_RANDOM_URL

    session = ClientSession()

    async with session.get(url, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.reply(f"`An error occurred, response code:` **{response.status}**")
            await session.close()
            return

    await session.close()

    if response['list']:
        response_word = response['list'][0]
    else:
        await event.reply(f"`No results for query:` **{udquery}**")
        return

    definition = f"**{response_word['word']}**: `{response_word['definition']}`"

    if response_word['example']:
        definition += f"\n\n**Example**: `{response_word['example']}`"

    definition = definition.replace("[", "").replace("]", "")

    if len(definition) >= 4096:
        file_io = io.BytesIO()
        file_io.write(bytes(definition.encode('utf-8')))
        file_io.name = f"definition of {response_word['word']}.txt"
        await event.reply(file=file_io, caption="`Output was too large, sent it as a file.`")
        return

    await event.reply(definition)
