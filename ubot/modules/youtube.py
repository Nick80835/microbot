# SPDX-License-Identifier: GPL-2.0-or-later

import pafy

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add("yt", userlocking=True)
async def youtube_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbest()
    try:
        await event.reply(file=video_stream.url)
    except:
        await event.reply(f"Download failed: [URL]({video_stream.url})")


@ldr.add("yta", userlocking=True)
async def youtube_audio_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbestaudio()
    try:
        await event.reply(file=video_stream.url)
    except:
        await event.reply(f"Download failed: [URL]({video_stream.url})")
