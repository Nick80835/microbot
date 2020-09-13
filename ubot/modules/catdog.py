# SPDX-License-Identifier: GPL-2.0-or-later

from ubot import ldr

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
    async with ldr.aioclient.get(CAT_URL, params=params, headers=CAT_HEADERS) as response:
        if response.status == 200:
            neko = await response.json()
        else:
            neko = response.status

    return neko


async def inu_atsume(params):
    async with ldr.aioclient.get(DOG_URL, params=params, headers=DOG_HEADERS) as response:
        if response.status == 200:
            inu = await response.json()
        else:
            inu = response.status

    return inu


async def shibe_inu_atsume():
    async with ldr.aioclient.get(SHIBE_URL, params=None, headers=None) as response:
        if response.status == 200:
            shibe_inu = await response.json()
        else:
            shibe_inu = response.status

    return shibe_inu


async def tori_atsume():
    async with ldr.aioclient.get(BIRD_URL, params=None, headers=None) as response:
        if response.status == 200:
            tori = await response.json()
        else:
            tori = response.status

    return tori


@ldr.add("shibe")
async def shibe(event):
    shibe_inu = await shibe_inu_atsume()

    if isinstance(shibe_inu, int):
        await event.edit(f"`There was an error finding the shibes! :( -> {shibe_inu}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), shibe_inu[0])
    await event.delete()


@ldr.add("bird")
async def bird(event):
    tori = await tori_atsume()

    if isinstance(tori, int):
        await event.edit(f"`There was an error finding the birdies! :( -> {tori}`")
        return

    await event.client.send_file(await event.client.get_input_entity(event.chat_id), tori[0])
    await event.delete()


@ldr.add_list(["cat", "pussy"], pattern_extra="(gif|)(f|)")
async def cat(event):
    neko = await neko_atsume(GIFPARAM if event.other_args[0] else IMGPARAM)

    if isinstance(neko, int):
        await event.reply(f"There was an error finding the cats! :( -> **{neko}**")
        return

    await event.client.send_file(event.chat, neko[0]["url"], force_document=bool(event.other_args[1]))
    await event.delete()


@ldr.add_list(["dog", "bitch"], pattern_extra="(gif|)(f|)")
async def dog(event):
    inu = await inu_atsume(GIFPARAM if event.other_args[0] else IMGPARAM)

    if isinstance(inu, int):
        await event.edit(f"There was an error finding the dogs! :( -> **{inu}**")
        return

    await event.client.send_file(event.chat, inu[0]["url"], force_document=bool(event.other_args[1]))
    await event.delete()
