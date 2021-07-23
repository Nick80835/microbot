import schizogif
import os
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from io import BytesIO
from ubot import ldr

@ldr.add("schizo", help="schizogif")
async def schizo_gif(event):
    reply = await event.get_reply_message()
    if reply.media:
        await event.client.download_media(reply.media, "tmp.mp4")
        gif = await ldr.run_async(generate_gif, event.args)
        await event.respond("", file=gif, force_document=True)

def generate_gif(text):
    os.system('ffmpeg -y -i tmp.mp4 -filter:v "setpts=0.1*PTS" -r 30 tmp.gif')
    os.remove('tmp.mp4')
    gif = BytesIO(schizogif.generate_gif(open('tmp.gif', 'rb').read(), text))
    os.remove('tmp.gif')
    gif.name = "sex.gif"
    return gif