# SPDX-License-Identifier: GPL-2.0-or-later

# Original source for the deepfrying code (used under the following license): https://github.com/Ovyerus/deeppyer

# MIT License
#
# Copyright (c) 2017 Ovyerus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import io
from random import randint, uniform

from PIL import Image, ImageEnhance, ImageOps
from telethon.tl.types import DocumentAttributeFilename

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add("deepfry")
async def deepfryer(event):
    try:
        frycount = int(event.args)
        if frycount < 1:
            frycount = 1
        elif frycount > 10:
            frycount = 10
    except ValueError:
        frycount = 1

    replied_fry = True

    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await ldr.get_image(reply_message)

        if isinstance(data, bool):
            await event.reply("`I can't deep fry that!`")
            return
    else:
        data = await ldr.get_image(event)
        replied_fry = False

        if isinstance(data, bool):
            await event.reply("`Reply to an image or sticker or caption an image to deep fry it!`")
            return

    # Download photo (highres) as byte array
    image = io.BytesIO()
    await event.client.download_media(data, image)
    image = Image.open(image)

    # Fry the image
    image = image.convert("RGB")

    for _ in range(frycount):
        image = await deepfry(image)

    fried_io = io.BytesIO()
    fried_io.name = "image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)

    if replied_fry:
        await reply_message.reply(file=fried_io)
    else:
        await event.reply(file=fried_io)


async def deepfry(img):
    # Crush image to hell and back
    img = ImageOps.posterize(img, randint(3, 7))

    # Generate colour overlay
    overlay = img.copy()
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(0.7, 1.8))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(0.8, 1.3))
    overlay = ImageEnhance.Color(overlay).enhance(uniform(0.7, 1.4))

    # Blend random colors onto and sharpen the image
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 200))

    return img
