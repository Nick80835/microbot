# SPDX-License-Identifier: GPL-2.0-or-later

import io
import textwrap

from PIL import Image, ImageDraw, ImageFont

from ubot import ldr


@ldr.add("color")
async def stickcolor(event):
    if not event.args:
        await event.edit(f"`Specify a valid color, use #colorhex or a color name.`")
        return

    try:
        image = Image.new("RGBA", (512, 512), event.args)
    except:
        try:
            image = Image.new("RGBA", (512, 512), "#" + event.args)
        except:
            await event.edit(f"**{event.args}**` is an invalid color, use #colorhex or a color name.`")
            return

    await event.delete()
    image_stream = io.BytesIO()
    image_stream.name = "sticker.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)
    await event.client.send_file(event.chat_id, image_stream)


@ldr.add("slet")
async def sticklet(event):
    sticktext = await ldr.get_text(event)

    if not sticktext:
        await event.edit("`I need text to sticklet!`")
        return

    await event.delete()

    sticktext = find_optimal_wrap(sticktext)
    sticktext = '\n'.join(sticktext)

    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230
    font = ImageFont.truetype("ubot/resources/Roboto-Regular.ttf", size=fontsize)

    while True:
        current_size = draw.multiline_textsize(sticktext, font=font, stroke_width=6, spacing=-10)

        if current_size[0] > 512 or current_size[1] > 512-64:
            fontsize -= 3
            font = ImageFont.truetype("ubot/resources/Roboto-Regular.ttf", size=fontsize)
        else:
            break

    width, height = draw.multiline_textsize(sticktext, font=font, stroke_width=6, spacing=-10)
    image = Image.new("RGBA", (512, height+64), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.multiline_text((int((512 - width) / 2), 0), sticktext, font=font, fill="white", stroke_width=6, stroke_fill="black", spacing=-10)
    bbox = image.getbbox()
    image = image.crop((0, bbox[1], 512, bbox[3]))

    image_stream = io.BytesIO()
    image_stream.name = "sticker.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)

    await event.client.send_file(event.chat_id, image_stream)


def find_optimal_wrap(text):
    chicken_wrap = int(len(text) / 18) or 20
    wrapped_text = textwrap.wrap(text, width=chicken_wrap)

    while len(wrapped_text)*3 > chicken_wrap:
        chicken_wrap += 1
        wrapped_text = textwrap.wrap(text, width=chicken_wrap)

    return wrapped_text
