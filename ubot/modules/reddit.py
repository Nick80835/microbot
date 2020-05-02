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
        if i.selftext and not i.permalink in i.url:
            return i.selftext, i.title

    return None, None


async def imagefetcher(event, sub):
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
            elif "v.redd.it" in post.url:
                image_url = post.media['reddit_video']['fallback_url'].split("?")[0]
                title = post.title
                break

    if not image_url:
        await event.reply(f"`Failed to find any valid content on `**r/{sub}**`!`")
        return

    try:
        await event.reply(title, file=image_url)
    except:
        await event.reply(f"`Failed to download content from `**r/{sub}**`!`\n`Title: `**{title}**\n`URL: `{image_url}")


async def titlefetcher(event, sub):
    post = REDDIT.subreddit(sub).random()

    if not post:
        title = await titlefetcherfallback(sub)
    else:
        title = post.title

    await event.reply(title)


async def bodyfetcher(event, sub):
    for _ in range(10):
        post = REDDIT.subreddit(sub).random()
        body = None

        if not post:
            body, title = await bodyfetcherfallback(sub)
        elif post.selftext and not post.permalink is post.url:
            body = post.selftext
            title = post.title

        if not body:
            continue

        await event.reply(f"**{title}**\n\n{body}")
        return
    
    await event.reply(f"`Failed to find any valid content on `**r/{sub}**`!`")


@ldr.add(pattern="redi")
async def redimg(event):
    sub = event.args.replace(" ", "_")

    if sub:
        await imagefetcher(event, sub)
    else:
        await event.reply("Syntax: .redi <subreddit name>")


@ldr.add(pattern="redt")
async def redtit(event):
    sub = event.args.replace(" ", "_")

    if sub:
        await titlefetcher(event, sub)
    else:
        await event.reply("Syntax: .redt <subreddit name>")


@ldr.add(pattern="redb")
async def redbod(event):
    sub = event.args.replace(" ", "_")

    if sub:
        await bodyfetcher(event, sub)
    else:
        await event.reply("Syntax: .redb <subreddit name>")


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
