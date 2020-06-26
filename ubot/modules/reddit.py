# SPDX-License-Identifier: GPL-2.0-or-later

import praw
from prawcore import exceptions as redex

from ubot.micro_bot import ldr

REDDIT = praw.Reddit(client_id='-fmzwojFG6JkGg',
                     client_secret=None,
                     user_agent='TG_Userbot')

VALID_ENDS = (".mp4", ".jpg", ".jpeg", ".png", ".gif")


async def imagefetcherfallback(sub):
    random_rising = REDDIT.subreddit(sub).random_rising(limit=10)

    for post in random_rising.__iter__():
        if post.url and post.url.endswith(VALID_ENDS):
            return post

    return None


async def titlefetcherfallback(sub):
    random_rising = REDDIT.subreddit(sub).random_rising(limit=1)
    return list(random_rising.__iter__())[0]


async def bodyfetcherfallback(sub):
    random_rising = REDDIT.subreddit(sub).random_rising(limit=10)

    for post in random_rising.__iter__():
        if post.selftext and not post.permalink in post.url:
            return post

    return None


async def imagefetcher(event, sub):
    image_url = False

    for _ in range(10):
        try:
            post = REDDIT.subreddit(sub).random() or await imagefetcherfallback(sub)
            post.title

            if event.nsfw_disabled and post.over_18:
                continue
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


@ldr.add("red(i|t|b)", userlocking=True, pass_nsfw=True)
async def redimg(event):
    sub = event.args.replace(" ", "_")
    fetch_type = event.other_args[0]

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


@ldr.add("jon(x|)", userlocking=True, pass_nsfw=True)
async def imsorryjon(event):
    if "x" in event.other_args[0]:
        sub = "ImReallySorryJon"
    else:
        sub = "ImSorryJon"

    await imagefetcher(event, sub)


@ldr.add("tihi", userlocking=True, pass_nsfw=True)
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")


@ldr.add("gab", userlocking=True, pass_nsfw=True)
async def tenma(event):
    await imagefetcher(event, "tenma")


@ldr.add("pourn", userlocking=True, pass_nsfw=True)
async def pourn(event):
    await imagefetcher(event, "PourPainting")
