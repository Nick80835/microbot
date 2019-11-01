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
    text_arg = event.pattern_match.group(1)

    if text_arg:
        pass
    elif event.is_reply:
        reply = await event.get_reply_message()
        text_arg = reply.text
    else:
        text_arg = "Give me some text to fuck it up!"

    cp_text = ""

    text_arg = await shitpostify(text_arg)
    text_arg = await mockify(text_arg)

    for letter in text_arg:
        if letter.lower() == "b":
            cp_text += b_emoji
        elif letter.lower() == "a":
            cp_text += a_emoji
        elif letter.lower() == "i":
            cp_text += i_emoji
        elif letter == " ":
            cp_text += choice(emoji)
        else:
            cp_text += letter

    await event.edit(cp_text)


@ldr.add(pattern="mock")
async def mock(event):
    text_arg = event.pattern_match.group(1)

    if text_arg:
        pass
    elif event.is_reply:
        reply = await event.get_reply_message()
        text_arg = reply.text
    else:
        text_arg = "Give me some text to fuck it up!"

    mock_text = await mockify(text_arg)

    await event.edit(mock_text)


async def shitpostify(text):
    text = text.replace("ck", "cc")
    text = text.replace("lol", "honk honk")
    text = text.replace("though", "tho")
    text = text.replace("cat", "pussy")
    text = text.replace("dark", "dank")
    text = text.replace("dick", "peepee")

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
