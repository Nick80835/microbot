import io

from PIL import Image

from ubot import ldr


@ldr.add("color")
async def stickcolor(event):
    if not event.args:
        await event.reply("Specify a valid color, use #colorhex or a color name.")
        return

    color_sticker = await ldr.run_async(stickcolorsync, event.args)

    if color_sticker:
        await event.reply(file=color_sticker)
    else:
        await event.reply(f"**{event.args}** is an invalid color, use #colorhex or a color name.")


def stickcolorsync(color):
    try:
        image = Image.new("RGBA", (512, 512), color)
    except:
        try:
            image = Image.new("RGBA", (512, 512), "#" + color)
        except:
            return

    image_stream = io.BytesIO()
    image_stream.name = "sticker.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)

    return image_stream
