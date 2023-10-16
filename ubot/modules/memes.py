# SPDX-License-Identifier: GPL-2.0-or-later

from asyncio import sleep
from random import choice, randint

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader

emoji = list("😂😝🤪🤩😤🥵🤯🥶😱🤔😩🙄💀👻🤡😹👀👁👌💦🔥🌚🌝🌞🔫💯")
b_emoji = "🅱️"
a_emoji = "🅰️"
i_emoji = "ℹ️"

owo_faces = "owo uwu owu uwo u-u o-o OwO UwU @-@ ;-; ;_; ._. (._.) (o-o) ('._.) (｡◕‿‿◕｡)" \
    " (｡◕‿◕｡) (─‿‿─) ◔⌣◔ ◉_◉".split(sep=" ")

zal_chars = " ̷̡̛̮͇̝͉̫̭͈͗͂̎͌̒̉̋́͜ ̵̠͕͍̩̟͚͍̞̳̌́̀̑̐̇̎̚͝ ̸̻̠̮̬̻͇͈̮̯̋̄͛̊͋̐̇͝͠ ̵̧̟͎͈̪̜̫̪͖̎͛̀͋͗́̍̊͠ ̵͍͉̟͕͇͎̖̹̔͌̊̏̌̽́̈́͊ͅ ̷̥͚̼̬̦͓͇̗͕͊̏͂͆̈̀̚͘̚ ̵̢̨̗̝̳͉̱̦͖̔̾͒͊͒̎̂̎͝ ̵̞̜̭̦̖̺͉̞̃͂͋̒̋͂̈́͘̕͜ ̶̢̢͇̲̥̗̟̏͛̇̏̊̑̌̔̚ͅͅ ̷̮͖͚̦̦̞̱̠̰̍̆̐͆͆͆̈̌́ ̶̲͚̪̪̪͍̹̜̬͊̆͋̄͒̾͆͝͝ ̴̨̛͍͖͎̞͍̞͕̟͑͊̉͗͑͆͘̕ ̶͕̪̞̲̘̬͖̙̞̽͌͗̽̒͋̾̍̀ ̵̨̧̡̧̖͔̞̠̝̌̂̐̉̊̈́́̑̓ ̶̛̱̼̗̱̙͖̳̬͇̽̈̀̀̎̋͌͝ ̷̧̺͈̫̖̖͈̱͎͋͌̆̈̃̐́̀̈".replace(" ", "")


@ldr.add("cp")
async def copypasta(event):
    text_arg, reply = await get_text_arg(event)

    text_arg = await shitpostify(text_arg)
    text_arg = await mockify(text_arg)
    text_arg = await emojify(text_arg)
    cp_text = await vaporize(text_arg)

    if reply:
        await reply.reply(cp_text)
    else:
        await event.reply(cp_text)


@ldr.add("mock")
async def mock(event):
    text_arg, reply = await get_text_arg(event)

    mock_text = await mockify(text_arg)

    if reply:
        await reply.reply(mock_text)
    else:
        await event.reply(mock_text)


@ldr.add("vap")
async def vapor(event):
    text_arg, reply = await get_text_arg(event)

    vapor_text = await vaporize(text_arg)

    if reply:
        await reply.reply(vapor_text)
    else:
        await event.reply(vapor_text)


@ldr.add("pop")
async def popifycmd(event):
    text_arg, reply = await get_text_arg(event)

    pop_text = await popify(text_arg)

    if reply:
        await reply.reply(pop_text)
    else:
        await event.reply(pop_text)


@ldr.add("cheem")
async def cheemifycmd(event):
    text_arg, reply = await get_text_arg(event)

    cheems_text = await cheemify(text_arg)

    if reply:
        await reply.reply(cheems_text)
    else:
        await event.reply(cheems_text)


@ldr.add("zal")
async def zalgo(event):
    text_arg, reply = await get_text_arg(event)

    zalgo_text = await zalgofy(text_arg)

    if reply:
        await reply.reply(zalgo_text)
    else:
        await event.reply(zalgo_text)


@ldr.add("owo")
async def owo(event):
    text_arg, reply = await get_text_arg(event)

    owo_text = await owoify(text_arg)

    if reply:
        await reply.reply(owo_text)
    else:
        await event.reply(owo_text)


async def get_text_arg(event):
    text_arg = event.args
    reply = False

    if text_arg:
        pass
    elif event.is_reply:
        reply = await event.get_reply_message()
        text_arg = reply.text
    else:
        text_arg = "Give me some text to fuck it up!"

    return text_arg, reply


async def shitpostify(text):
    text = text.replace("dick", "peepee")
    text = text.replace("ck", "cc")
    text = text.replace("lol", "honk honk")
    text = text.replace("though", "tho")
    text = text.replace("cat", "pussy")
    text = text.replace("dark", "dank")

    return text


async def popify(text):
    text = text.replace(" ", "!_")

    return text


async def cheemify(text):
    text = text.replace("ese", "ms")
    text = text.replace("se", "mse")
    text = text.replace("ck", "mk")
    text = text.replace("ake", "amke")
    text = text.replace("as", "ams")
    text = text.replace("n", "m")
    text = text.replace("ab", "amb")
    text = text.replace("lp", "lmp")
    text = text.replace("ke", "mke")
    text = text.replace("ec", "emc")
    text = text.replace("ig", "img")
    text = text.replace("ob", "omb")
    text = text.replace("pep", "pemp")
    text = text.replace("pop", "pomp")
    text = text.replace("rib", "rimb")

    return text


async def mockify(text):
    mock_text = ""

    for letter in text:
        if choice([True, False]):
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
    text = text.replace("AB", "🆎")
    text = text.replace("CL", "🆑")
    text = text.replace("B", "🅱️")
    text = text.replace("A", "🅰️")
    text = text.replace("I", "ℹ️")

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


async def owoify(text):
    text = text.replace("r", "w")
    text = text.replace("R", "W")
    text = text.replace("n", "ny")
    text = text.replace("N", "NY")
    text = text.replace("ll", "w")
    text = text.replace("LL", "W")
    text = text.replace("l", "w")
    text = text.replace("L", "W")

    text += f" {choice(owo_faces)}"

    return text


async def zalgofy(text):
    zalgo_text = ""

    for letter in text:
        if letter == " ":
            zalgo_text += letter
            continue

        letter += choice(zal_chars)
        letter += choice(zal_chars)
        letter += choice(zal_chars)
        zalgo_text += letter

    return zalgo_text
