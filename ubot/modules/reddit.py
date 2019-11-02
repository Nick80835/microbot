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
import mimetypes
from random import choice

import praw
from aiohttp import ClientSession

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

REDDIT = praw.Reddit(client_id='-fmzwojFG6JkGg',
                     client_secret=None,
                     user_agent='TG_Userbot')

VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


async def imagefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())

    for _ in range(10):
        post = choice(hot_list)

        if post.url:
            if post.url.endswith(VALID_ENDS):
                return post.url, post.title

    return None, None


async def titlefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())

    return choice(hot_list).title


async def imagefetcher(event, sub):
    await event.edit(f"`Fetching from `**r/{sub}**`…`")
    image_url = False

    for _ in range(10):
        post = REDDIT.subreddit(sub).random()

        if not post:
            image_url, title = await imagefetcherfallback(sub)
            break

        if post.url:
            if post.url.endswith(VALID_ENDS):
                image_url = post.url
                title = post.title
                break

    if not image_url:
        await event.edit(f"`Failed to find any valid content on `**r/{sub}**`!`")
        return

    try:
        image_io = io.BytesIO()
        session = ClientSession()

        async with session.get(image_url) as response:
            if response.status == 200:
                image_io.write(await response.read())
                image_io.name = f"reddit_content{mimetypes.guess_extension(response.headers['content-type'])}"
                image_io.seek(0)
            else:
                raise Exception

        await session.close()
        await event.reply(title, file=image_io)
    except:
        await session.close()
        await event.edit(f"`Failed to download content from `**r/{sub}**`!`")


async def titlefetcher(event, sub):
    await event.edit(f"`Fetching from `**r/{sub}**`…`")

    post = REDDIT.subreddit(sub).random()

    if not post:
        title = await titlefetcherfallback(sub)
    else:
        title = post.title

    await event.reply(title)


@ldr.add(pattern="redi")
async def redimg(event):
    sub = event.pattern_match.group(1)

    if sub:
        await imagefetcher(event, sub)
    else:
        await event.edit("Syntax: .redi <subreddit name>")


@ldr.add(pattern="redt")
async def redtit(event):
    sub = event.pattern_match.group(1)

    if sub:
        await titlefetcher(event, sub)
    else:
        await event.edit("Syntax: .redt <subreddit name>")


@ldr.add(pattern="suffer")
async def makemesuffer(event):
    await imagefetcher(event, "MakeMeSuffer")


@ldr.add(pattern="snafu")
async def coaxedintoasnafu(event):
    await imagefetcher(event, "CoaxedIntoASnafu")


@ldr.add(pattern="aita")
async def amitheasshole(event):
    await titlefetcher(event, "AmITheAsshole")


@ldr.add(pattern="jon(x|)")
async def imsorryjon(event):
    if "x" in event.pattern_match.group(0):
        sub = "ImReallySorryJon"
    else:
        sub = "ImSorryJon"

    await imagefetcher(event, sub)


@ldr.add(pattern="tihi")
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")
