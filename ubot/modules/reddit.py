import asyncpraw
from asyncprawcore import exceptions as redex

from ubot import ldr

REDDIT = asyncpraw.Reddit(client_id='-fmzwojFG6JkGg',
                          client_secret=None,
                          user_agent='TG_Userbot')

VALID_ENDS = (".mp4", ".jpg", ".jpeg", "jpe", ".png", ".gif")


async def imagefetcherfallback(subreddit):
    async for post in subreddit.random_rising(limit=10):
        if post.url and post.url.endswith(VALID_ENDS):
            return post


async def titlefetcherfallback(subreddit):
    async for post in subreddit.random_rising(limit=1):
        return post


async def bodyfetcherfallback(subreddit):
    async for post in subreddit.random_rising(limit=10):
        if post.selftext and not post.permalink is post.url:
            return post


async def imagefetcher(event, sub):
    image_url = False
    subreddit = await REDDIT.subreddit(sub)

    for _ in range(10):
        try:
            post = await subreddit.random() or await imagefetcherfallback(subreddit)
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
    subreddit = await REDDIT.subreddit(sub)

    try:
        post = await subreddit.random() or await titlefetcherfallback(subreddit)
        post.title
    except redex.Forbidden:
        await event.reply(f"**r/{sub}** is private!")
        return
    except (redex.NotFound, KeyError):
        await event.reply(f"**r/{sub}** doesn't exist!")
        return
    except AttributeError:
        await event.reply(f"Failed to find any valid content on **r/{sub}**!")
        return

    await event.reply(post.title)


async def bodyfetcher(event, sub):
    subreddit = await REDDIT.subreddit(sub)

    for _ in range(10):
        try:
            post = await subreddit.random() or await bodyfetcherfallback(subreddit)
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


@ldr.add("redi", userlocking=True, pass_nsfw=True, help="Fetches images from Reddit, requires a subreddit name as an argument.")
@ldr.add("redb", userlocking=True, pass_nsfw=True, help="Fetches text from Reddit, requires a subreddit name as an argument.")
@ldr.add("redt", userlocking=True, pass_nsfw=True, help="Fetches titles from Reddit, requires a subreddit name as an argument.")
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


reddit_images = {
    "suffer": "MakeMeSuffer",
    "snafu": "CoaxedIntoASnafu",
    "jon": "ImSorryJon",
    "jonx": "ImReallySorryJon",
    "tihi": "TIHI",
    "gab": "Tenma",
    "pourn": "PourPainting",
    "monke": "Ape",
    "meme": "DankMemes",
    "okbr": "OKBuddyRetard",
    "comedy": "ComedyNecrophilia",
    "reddit": "RedditMoment",
    "heartdisease": "Chonkers"
}

reddit_bodies = {
    "aita": "AmITheAsshole",
    "tifu": "TIFU"
}


@ldr.add_dict(reddit_images, userlocking=True, pass_nsfw=True)
async def quick_reddit_image(event):
    await imagefetcher(event, event.extra)


@ldr.add_dict(reddit_bodies, userlocking=True, pass_nsfw=True)
async def quick_reddit_body(event):
    await bodyfetcher(event, event.extra)
