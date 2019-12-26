# Copyright (C) 2019 Nick Filmer (nick80835@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io
import textwrap

from PIL import Image, ImageDraw, ImageFont

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="slet")
async def sticklet(event):
    sticktext = event.pattern_match.group(1)

    if not sticktext:
        await event.edit("`I need text to sticklet!`")
        return

    await event.delete()

    sticktext = textwrap.wrap(sticktext, width=20)
    sticktext = '\n'.join(sticktext)

    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230
    font = ImageFont.truetype("ubot/resources/RobotoMono-Regular.ttf", size=fontsize)

    while True:
        current_size = draw.multiline_textsize(sticktext, font=font, stroke_width=8, spacing=-10)

        if current_size[0] > 512 or current_size[1] > 512:
            fontsize -= 3
            font = ImageFont.truetype("ubot/resources/RobotoMono-Regular.ttf", size=fontsize)
        else:
            break

    width, height = draw.multiline_textsize(sticktext, font=font, stroke_width=8, spacing=-10)
    image = Image.new("RGBA", (512, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    draw.multiline_text(((512-width)/2, -10), sticktext, font=font, fill="white", stroke_width=8, stroke_fill="black", spacing=-10)

    image_stream = io.BytesIO()
    image_stream.name = "sticker.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)

    await event.client.send_file(event.chat_id, image_stream)
