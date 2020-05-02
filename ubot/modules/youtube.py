# SPDX-License-Identifier: GPL-2.0-or-later

import pafy

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="yt")
async def youtube_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbest()
    try:
        await event.client.send_file(event.chat_id, file=video_stream.url)
    except:
        await event.reply(f"`Download failed: `[URL]({video_stream.url})")


@ldr.add(pattern="yta")
async def youtube_audio_cmd(event):
    video = pafy.new(event.args)
    video_stream = video.getbestaudio()
    try:
        await event.client.send_file(event.chat_id, file=video_stream.url)
    except:
        await event.reply(f"`Download failed: `[URL]({video_stream.url})")
