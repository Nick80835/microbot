# SPDX-License-Identifier: GPL-2.0-or-later

import asyncpraw
from asyncprawcore import exceptions as redex

from ubot.micro_bot import ldr

REDDIT = asyncpraw.Reddit(client_id='-fmzwojFG6JkGg',
                          client_secret=None,
                          user_agent='TG_Userbot')

VALID_ENDS = (".mp4", ".jpg", ".jpeg", "jpe", ".png", ".gif")


async def imagefetcherfallback(subreddit):
    async for post in subreddit.random_rising(limit=10):
        if post.url and post.url.endswith(VALID_ENDS):
            return post

    return None


async def titlefetcherfallback(subreddit):
    async for post in subreddit.random_rising(limit=1):
        return post


async def bodyfetcherfallback(subreddit):
    async for post in subreddit.random_rising(limit=10):
        if post.selftext and not post.permalink is post.url:
            return post

    return None


async def imagefetcher(event, sub):
    image_url = False

    try:
        subreddit = await REDDIT.subreddit(sub)
    except redex.Forbidden:
        await event.reply(f"**r/{sub}** is private!")
        return
    except (redex.NotFound, KeyError):
        await event.reply(f"**r/{sub}** doesn't exist!")
        return

    for _ in range(10):
        try:
            post = await subreddit.random() or await imagefetcherfallback(subreddit)
            post.title

            if event.nsfw_disabled and post.over_18:
                continue
        except AttributeError:
            continue

        if post.url and post.url.endswith(VALID_ENDS):
            image_url = post.url
            title = post.title
            break

    if not image_url:
        await event.reply(f"Failed to find any valid content on **r/{sub}**!")
        return

    try:
        await event.reply(title, file=image_url)
    except:
        await event.reply(f"Failed to download content from **r/{sub}**!\nTitle: **{title}**\nURL: {image_url}")


async def titlefetcher(event, sub):
    try:
        subreddit = await REDDIT.subreddit(sub)
    except redex.Forbidden:
        await event.reply(f"**r/{sub}** is private!")
        return
    except (redex.NotFound, KeyError):
        await event.reply(f"**r/{sub}** doesn't exist!")
        return

    post = await subreddit.random() or await titlefetcherfallback(subreddit)

    await event.reply(post.title)


async def bodyfetcher(event, sub):
    try:
        subreddit = await REDDIT.subreddit(sub)
    except redex.Forbidden:
        await event.reply(f"**r/{sub}** is private!")
        return
    except (redex.NotFound, KeyError):
        await event.reply(f"**r/{sub}** doesn't exist!")
        return

    for _ in range(10):
        try:
            post = await subreddit.random() or await bodyfetcherfallback(subreddit)
            post.title
        except AttributeError:
            continue

        body = None

        if post.selftext and not post.permalink is post.url:
            body = post.selftext
            title = post.title

        if not body:
            continue

        await event.reply(f"**{title}**\n\n{body}")
        return

    await event.reply(f"Failed to find any valid content on **r/{sub}**!")


@ldr.add_list(["redi", "redb", "redt"], userlocking=True, pass_nsfw=True)
async def redimg(event):
    sub = event.args.replace(" ", "_")
    fetch_type = event.command[-1]

    if not sub:
        await event.reply(f"Syntax: {ldr.prefix()}red(i|t|b) <subreddit name>")
        return

    if fetch_type == "i":
        await imagefetcher(event, sub)
    elif fetch_type == "t":
        await titlefetcher(event, sub)
    elif fetch_type == "b":
        await bodyfetcher(event, sub)


@ldr.add("suffer", userlocking=True, pass_nsfw=True)
async def makemesuffer(event):
    await imagefetcher(event, "MakeMeSuffer")


@ldr.add("snafu", userlocking=True, pass_nsfw=True)
async def coaxedintoasnafu(event):
    await imagefetcher(event, "CoaxedIntoASnafu")


@ldr.add("aita", userlocking=True, pass_nsfw=True)
async def amitheasshole(event):
    await bodyfetcher(event, "AmITheAsshole")


@ldr.add("tifu", userlocking=True, pass_nsfw=True)
async def todayifuckedup(event):
    await bodyfetcher(event, "TIFU")


@ldr.add_list(["jon", "jonx"], userlocking=True, pass_nsfw=True)
async def imsorryjon(event):
    if event.command[-1] == "x":
        await imagefetcher(event, "ImReallySorryJon")
    else:
        await imagefetcher(event, "ImSorryJon")


@ldr.add("tihi", userlocking=True, pass_nsfw=True)
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")


@ldr.add("gab", userlocking=True, pass_nsfw=True)
async def tenma(event):
    await imagefetcher(event, "tenma")


@ldr.add("pourn", userlocking=True, pass_nsfw=True)
async def pourn(event):
    await imagefetcher(event, "PourPainting")
