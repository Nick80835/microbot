# SPDX-License-Identifier: GPL-2.0-or-later

import io
from random import choice, shuffle

import praw
from prawcore import exceptions as redex

from ubot.micro_bot import ldr

REDDIT = praw.Reddit(client_id='-fmzwojFG6JkGg',
                     client_secret=None,
                     user_agent='TG_Userbot')

VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


async def imagefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())
    shuffle(hot_list)

    for post in hot_list:
        if post.url and post.url.endswith(VALID_ENDS):
            return post

    return None


async def titlefetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    return choice(list(hot.__iter__()))


async def bodyfetcherfallback(sub):
    hot = REDDIT.subreddit(sub).hot()
    hot_list = list(hot.__iter__())
    shuffle(hot_list)

    for post in hot_list:
        if post.selftext and not post.permalink in post.url:
            return post

    return None


async def imagefetcher(event, sub):
    image_url = False

    for _ in range(10):
        try:
            post = REDDIT.subreddit(sub).random() or await imagefetcherfallback(sub)
            post.title
        except redex.Forbidden:
            await event.reply(f"**r/{sub}** is private!")
            return
        except (redex.NotFound, KeyError):
            await event.reply(f"**r/{sub}** doesn't exist!")
            return
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
        post = REDDIT.subreddit(sub).random() or await titlefetcherfallback(sub)
        post.title
    except redex.Forbidden:
        await event.reply(f"**r/{sub}** is private!")
        return
    except (redex.NotFound, KeyError):
        await event.reply(f"**r/{sub}** doesn't exist!")
        return

    await event.reply(post.title)


async def bodyfetcher(event, sub):
    for _ in range(10):
        try:
            post = REDDIT.subreddit(sub).random() or await bodyfetcherfallback(sub)
            post.title
        except redex.Forbidden:
            await event.reply(f"**r/{sub}** is private!")
            return
        except (redex.NotFound, KeyError):
            await event.reply(f"**r/{sub}** doesn't exist!")
            return
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


@ldr.add("red(i|t|b)", userlocking=True)
async def redimg(event):
    sub = event.args.replace(" ", "_")
    fetch_type = event.pattern_match.group(1)

    if not sub:
        await event.reply(f"Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}red(i|t|b) <subreddit name>")
        return

    if fetch_type == "i":
        await imagefetcher(event, sub)
    elif fetch_type == "t":
        await titlefetcher(event, sub)
    elif fetch_type == "b":
        await bodyfetcher(event, sub)


@ldr.add("suffer", userlocking=True)
async def makemesuffer(event):
    await imagefetcher(event, "MakeMeSuffer")


@ldr.add("snafu", userlocking=True)
async def coaxedintoasnafu(event):
    await imagefetcher(event, "CoaxedIntoASnafu")


@ldr.add("aita", userlocking=True)
async def amitheasshole(event):
    await bodyfetcher(event, "AmITheAsshole")


@ldr.add("tifu", userlocking=True)
async def todayifuckedup(event):
    await bodyfetcher(event, "TIFU")


@ldr.add("jon(x|)", userlocking=True)
async def imsorryjon(event):
    if "x" in event.pattern_match.group(0):
        sub = "ImReallySorryJon"
    else:
        sub = "ImSorryJon"

    await imagefetcher(event, sub)


@ldr.add("tihi", userlocking=True)
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")


@ldr.add("gab", userlocking=True)
async def tenma(event):
    await imagefetcher(event, "tenma")
