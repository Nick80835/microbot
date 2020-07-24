# SPDX-License-Identifier: GPL-2.0-or-later

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
    await event.edit(f"`Fetching image from `**r/{sub}**`…`")
    image_url = False

    for _ in range(10):
        try:
            post = REDDIT.subreddit(sub).random() or await imagefetcherfallback(sub)
            post.title
        except redex.Forbidden:
            await event.edit(f"**r/{sub}**` is private!`")
            return
        except (redex.NotFound, KeyError):
            await event.edit(f"**r/{sub}**` doesn't exist!`")
            return
        except AttributeError:
            continue

        if post.url and post.url.endswith(VALID_ENDS):
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
    await event.edit(f"`Fetchingn title from `**r/{sub}**`…`")

    try:
        post = REDDIT.subreddit(sub).random() or await titlefetcherfallback(sub)
        post.title
    except redex.Forbidden:
        await event.edit(f"**r/{sub}**` is private!`")
        return
    except (redex.NotFound, KeyError):
        await event.edit(f"**r/{sub}**` doesn't exist!`")
        return

    await event.edit(post.title)


async def bodyfetcher(event, sub):
    await event.edit(f"`Fetching text from `**r/{sub}**`…`")

    for _ in range(10):
        try:
            post = REDDIT.subreddit(sub).random() or await bodyfetcherfallback(sub)
            post.title
        except redex.Forbidden:
            await event.edit(f"**r/{sub}**` is private!`")
            return
        except (redex.NotFound, KeyError):
            await event.edit(f"**r/{sub}**` doesn't exist!`")
            return
        except AttributeError:
            continue

        body = None

        if post.selftext and not post.permalink is post.url:
            body = post.selftext
            title = post.title

        if not body:
            continue

        await event.edit(f"**{title}**\n\n{body}")
        return

    await event.edit(f"`Failed to find any valid content on `**r/{sub}**`!`")


@ldr.add("redi", help="Fetches images from Reddit, requires a subreddit name as an argument.")
@ldr.add("redb", help="Fetches text from Reddit, requires a subreddit name as an argument.")
@ldr.add("redt", help="Fetches titles from Reddit, requires a subreddit name as an argument.")
async def reddit_fetcher(event):
    sub = event.args.replace(" ", "_")
    fetch_type = event.command[-1]

    if not sub:
        await event.edit(f"`Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}red(i|t|b) <subreddit name>`")
        return

    if fetch_type == "i":
        await imagefetcher(event, sub)
    elif fetch_type == "t":
        await titlefetcher(event, sub)
    elif fetch_type == "b":
        await bodyfetcher(event, sub)


@ldr.add("suffer")
async def makemesuffer(event):
    await imagefetcher(event, "MakeMeSuffer")


@ldr.add("snafu")
async def coaxedintoasnafu(event):
    await imagefetcher(event, "CoaxedIntoASnafu")


@ldr.add("aita")
async def amitheasshole(event):
    await bodyfetcher(event, "AmITheAsshole")


@ldr.add("tifu")
async def todayifuckedup(event):
    await bodyfetcher(event, "TIFU")


@ldr.add_list(["jon", "jonx"])
async def imsorryjon(event):
    if event.command[-1] == "x":
        await imagefetcher(event, "ImReallySorryJon")
    else:
        await imagefetcher(event, "ImSorryJon")


@ldr.add("tihi")
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")


@ldr.add("gab")
async def tenma(event):
    await imagefetcher(event, "tenma")


@ldr.add("pourn")
async def pourn(event):
    await imagefetcher(event, "PourPainting")
