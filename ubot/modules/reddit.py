# SPDX-License-Identifier: GPL-2.0-or-later

import io
from random import choice, shuffle

import praw
from prawcore import exceptions as redex

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

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
            await event.reply(f"**r/{sub}**` is private!`")
            return
        except (redex.NotFound, KeyError):
            await event.reply(f"**r/{sub}**` doesn't exist!`")
            return
        except AttributeError:
            continue

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
    try:
        post = REDDIT.subreddit(sub).random() or await titlefetcherfallback(sub)
        post.title
    except redex.Forbidden:
        await event.reply(f"**r/{sub}**` is private!`")
        return
    except (redex.NotFound, KeyError):
        await event.reply(f"**r/{sub}**` doesn't exist!`")
        return

    await event.reply(post.title)


async def bodyfetcher(event, sub):
    for _ in range(10):
        try:
            post = REDDIT.subreddit(sub).random() or await bodyfetcherfallback(sub)
            post.title
        except redex.Forbidden:
            await event.reply(f"**r/{sub}**` is private!`")
            return
        except (redex.NotFound, KeyError):
            await event.reply(f"**r/{sub}**` doesn't exist!`")
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
    
    await event.reply(f"`Failed to find any valid content on `**r/{sub}**`!`")


@ldr.add("redi")
async def redimg(event):
    sub = event.args.replace(" ", "_")

    if sub:
        await imagefetcher(event, sub)
    else:
        await event.reply("Syntax: .redi <subreddit name>")


@ldr.add("redt")
async def redtit(event):
    sub = event.args.replace(" ", "_")

    if sub:
        await titlefetcher(event, sub)
    else:
        await event.reply("Syntax: .redt <subreddit name>")


@ldr.add("redb")
async def redbod(event):
    sub = event.args.replace(" ", "_")

    if sub:
        await bodyfetcher(event, sub)
    else:
        await event.reply("Syntax: .redb <subreddit name>")


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


@ldr.add("jon(x|)")
async def imsorryjon(event):
    if "x" in event.pattern_match.group(0):
        sub = "ImReallySorryJon"
    else:
        sub = "ImSorryJon"

    await imagefetcher(event, sub)


@ldr.add("tihi")
async def thanksihateit(event):
    await imagefetcher(event, "TIHI")


@ldr.add("gab")
async def tenma(event):
    await imagefetcher(event, "tenma")
