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

from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

DAN_URL = "http://danbooru.donmai.us/posts.json"


@ldr.add(pattern="dan(s|x|q|)")
async def danbooru(event):
    if "x" in event.pattern_match.group(0):
        rating = "Rating:explicit"
    elif "s" in event.pattern_match.group(0):
        rating = "Rating:safe"
    elif "q" in event.pattern_match.group(0):
        rating = "Rating:questionable"
    else:
        rating = ""

    search_query = event.pattern_match.group(2)

    params = {"limit": 1,
              "random": "true",
              "tags": f"{rating} {search_query}".strip()}

    session = ClientSession()

    async with session.get(DAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.reply(f"`An error occurred, response code: `**{response.status}**")
            return

    await session.close()

    if not response:
        await event.reply(f"`No results for query: `**{search_query}**")
        return

    valid_urls = []

    for url in ['file_url', 'large_file_url', 'source']:
        if url in response[0].keys():
            valid_urls.append(response[0][url])

    if not valid_urls:
        await event.reply(f"`Failed to find URLs for query: `**{search_query}**")
        return

    for image_url in valid_urls:
        try:
            await event.reply(file=image_url)
            return
        except:
            pass

    await event.reply(f"`Failed to fetch media for query: `**{search_query}**")
