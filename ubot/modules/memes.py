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

from random import choice, randint

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

emoji = list("😂😝🤪🤩😤🥵🤯🥶😱🤔😩🙄💀👻🤡😹👀👁👌💦🔥🌚🌝🌞🔫💯")
b_emoji = "🅱️"
a_emoji = "🅰️"
i_emoji = "ℹ️"


@ldr.add(pattern="cp")
async def copypasta(event):
    text_arg = await get_text_arg(event)

    text_arg = await shitpostify(text_arg)
    text_arg = await mockify(text_arg)
    text_arg = await vaporize(text_arg)
    cp_text = await emojify(text_arg)

    await event.edit(cp_text)


@ldr.add(pattern="mock")
async def mock(event):
    text_arg = await get_text_arg(event)

    mock_text = await mockify(text_arg)

    await event.edit(mock_text)


@ldr.add(pattern="vap")
async def vapor(event):
    text_arg = await get_text_arg(event)

    vapor_text = await vaporize(text_arg)

    await event.edit(vapor_text)


async def get_text_arg(event):
    text_arg = event.pattern_match.group(1)

    if text_arg:
        pass
    elif event.is_reply:
        reply = await event.get_reply_message()
        text_arg = reply.text
    else:
        text_arg = "Give me some text to fuck it up!"

    return text_arg


async def shitpostify(text):
    text = text.replace("dick", "peepee")
    text = text.replace("ck", "cc")
    text = text.replace("lol", "honk honk")
    text = text.replace("though", "tho")
    text = text.replace("cat", "pussy")
    text = text.replace("dark", "dank")

    return text


async def mockify(text):
    mock_text = ""

    for letter in text:
        if len(mock_text) >= 2:
            if ''.join(mock_text[-2:-1]).islower():
                mock_text += letter.upper()
                continue

            if ''.join(mock_text[-2:-1]).isupper():
                mock_text += letter.lower()
                continue

        if randint(1, 2) == randint(1, 2):
            mock_text += letter.lower()
        else:
            mock_text += letter.upper()

    return mock_text


async def emojify(text):
    text = text.replace("ab", "🆎")
    text = text.replace("cl", "🆑")
    text = text.replace("b", "🅱️")
    text = text.replace("a", "🅰️")
    text = text.replace("i", "ℹ️")

    emoji_text = ""

    for letter in text:
        if letter == " ":
            emoji_text += choice(emoji)
        else:
            emoji_text += letter

    return emoji_text


async def vaporize(text):
    vapor_text = ""
    char_distance = 65248

    for letter in text:
        ord_letter = ord(letter)
        if ord('!') <= ord_letter <= ord('~'):
            letter = chr(ord_letter + char_distance)
        vapor_text += letter

    return vapor_text
