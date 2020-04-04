# SPDX-License-Identifier: GPL-2.0-or-later

import io
from random import choice, shuffle

import praw

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


async def bodyfetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())
    shuffle(hot_list)

    for i in hot_list:
        if i.selftext:
            return i.selftext, i.title

    return None, None


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
        await event.client.send_file(event.chat_id, image_url, caption=title)
        await event.delete()
    except:
        await event.edit(f"`Failed to download content from `**r/{sub}**`!`\n`Title: `**{title}**\n`URL: `{image_url}")


async def titlefetcher(event, sub):
    await event.edit(f"`Fetching from `**r/{sub}**`…`")

    post = REDDIT.subreddit(sub).random()

    if not post:
        title = await titlefetcherfallback(sub)
    else:
        title = post.title

    await event.reply(title)


async def bodyfetcher(event, sub):
    await event.edit(f"`Fetching from `**r/{sub}**`…`")

    for _ in range(10):
        post = REDDIT.subreddit(sub).random()

        if not post:
            body, title = await titlefetcherfallback(sub)
        elif post.selftext:
            body = post.selftext
            title = post.title

        if not body:
            continue

        await event.edit(f"**{title}**\n\n{body}")
        return
    
    await event.edit(f"`Failed to find any valid content on `**r/{sub}**`!`")


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


@ldr.add(pattern="redb")
async def redbod(event):
    sub = event.pattern_match.group(1)

    if sub:
        await bodyfetcher(event, sub)
    else:
        await event.edit("Syntax: .redb <subreddit name>")


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


@ldr.add(pattern="gab")
async def tenma(event):
    await imagefetcher(event, "tenma")
