# SPDX-License-Identifier: GPL-2.0-or-later

import io

from PIL import Image, ImageColor

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add("color")
async def stickcolor(event):
    if not event.args:
        await event.reply(f"`Specify a valid color, use #colorhex or a color name.`")
        return

    try:
        image = Image.new("RGBA", (512, 512), event.args)
    except:
        try:
            image = Image.new("RGBA", (512, 512), "#" + event.args)
        except:
            await event.reply(f"**{event.args}**` is an invalid color, use #colorhex or a color name.`")
            return

    image_stream = io.BytesIO()
    image_stream.name = "sticker.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)
    await event.reply(file=image_stream)
