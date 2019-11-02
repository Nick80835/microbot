# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

UD_QUERY_URL = 'http://api.urbandictionary.com/v0/define'
UD_RANDOM_URL = 'http://api.urbandictionary.com/v0/random'


@ldr.add(pattern="ud")
async def urban_dict(event):
    udquery = event.pattern_match.group(1)

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
            await event.edit(f"`An error occurred, response code:` **{response.status}**")
            return

    await session.close()

    if response['list']:
        response_word = response['list'][0]
    else:
        await event.edit(f"`No results for query:` **{udquery}**")
        return

    definition = f"**{response_word['word']}**: `{response_word['definition']}`"

    if response_word['example']:
        definition += f"\n\n**Example**: `{response_word['example']}`"

    definition = definition.replace("[", "").replace("]", "")

    if len(definition) >= 4096:
        file_io = io.BytesIO()
        file_io.write(bytes(definition.encode('utf-8')))
        file_io.name = f"definition of {response_word['word']}.txt"
        await event.client.send_file(event.chat_id, file_io, caption="`Output was too large, sent it as a file.`")
        await event.delete()
        return

    await event.edit(definition)
