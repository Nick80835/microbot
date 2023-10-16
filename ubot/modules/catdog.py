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

CAT_URL = 'http://api.thecatapi.com/v1/images/search'
DOG_URL = 'http://api.thedogapi.com/v1/images/search'
SHIBE_URL = 'http://shibe.online/api/shibes'
BIRD_URL = 'http://shibe.online/api/birds'
CAT_API_KEY = 'e5a56813-be40-481c-9c8a-a6585c37c1fe'
DOG_API_KEY = '105555df-5c50-40fe-bd59-d15a17ce1c2e'
CAT_HEADERS = {"x-api-key": CAT_API_KEY}
DOG_HEADERS = {"x-api-key": DOG_API_KEY}
IMGPARAM = {"mime_types": "jpg,png"}
GIFPARAM = {"mime_types": "gif"}


async def neko_atsume(params):
    session = ClientSession()

    async with session.get(CAT_URL, params=params, headers=CAT_HEADERS) as response:
        if response.status == 200:
            neko = await response.json()
        else:
            neko = response.status

    await session.close()
    return neko


async def inu_atsume(params):
    session = ClientSession()

    async with session.get(DOG_URL, params=params, headers=DOG_HEADERS) as response:
        if response.status == 200:
            inu = await response.json()
        else:
            inu = response.status

    await session.close()
    return inu


async def shibe_inu_atsume():
    session = ClientSession()

    async with session.get(SHIBE_URL, params=None, headers=None) as response:
        if response.status == 200:
            shibe_inu = await response.json()
        else:
            shibe_inu = response.status

    await session.close()
    return shibe_inu


async def tori_atsume():
    session = ClientSession()

    async with session.get(BIRD_URL, params=None, headers=None) as response:
        if response.status == 200:
            tori = await response.json()
        else:
            tori = response.status

    await session.close()
    return tori


@ldr.add(pattern="shibe")
async def shibe(event):
    shibe_inu = await shibe_inu_atsume()

    if isinstance(shibe_inu, int):
        await event.reply(f"`There was an error finding the shibes! :( -> {shibe_inu}`")
        return

    await event.reply(file=shibe_inu[0])


@ldr.add(pattern="bird")
async def bird(event):
    tori = await tori_atsume()

    if isinstance(tori, int):
        await event.reply(f"`There was an error finding the birdies! :( -> {tori}`")
        return

    await event.reply(file=tori[0])


@ldr.add(pattern="cat")
async def cat(event):
    neko = await neko_atsume(IMGPARAM)

    if isinstance(neko, int):
        await event.reply(f"`There was an error finding the cats! :( -> {neko}`")
        return

    await event.reply(file=neko[0]["url"])


@ldr.add(pattern="cathd")
async def cathd(event):
    neko = await neko_atsume(IMGPARAM)

    if isinstance(neko, int):
        await event.reply(f"`There was an error finding the cats! :( -> {neko}`")
        return

    await event.reply(file=neko[0]["url"], force_document=True)


@ldr.add(pattern="catgif")
async def catgif(event):
    neko = await neko_atsume(GIFPARAM)

    if isinstance(neko, int):
        await event.reply(f"`There was an error finding the cats! :( -> {neko}`")
        return

    await event.reply(file=neko[0]["url"])


@ldr.add(pattern="dog")
async def dog(event):
    inu = await inu_atsume(IMGPARAM)

    if isinstance(inu, int):
        await event.reply(f"`There was an error finding the dogs! :( -> {inu}`")
        return

    await event.reply(file=inu[0]["url"])


@ldr.add(pattern="doghd")
async def doghd(event):
    inu = await inu_atsume(IMGPARAM)

    if isinstance(inu, int):
        await event.reply(f"`There was an error finding the dogs! :( -> {inu}`")
        return

    await event.reply(file=inu[0]["url"], force_document=True).delete()


@ldr.add(pattern="doggif")
async def doggif(event):
    inu = await inu_atsume(GIFPARAM)

    if isinstance(inu, int):
        await event.reply(f"`There was an error finding the dogs! :( -> {inu}`")
        return

    await event.reply(file=inu[0]["url"])
