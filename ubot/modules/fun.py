# SPDX-License-Identifier: GPL-2.0-or-later

from random import choice

from ubot.micro_bot import ldr

bot_name = ldr.settings.get_config("bot_name") or "bot"

yesno_answers = [
    "Yes!", "Yup!", "Yeah!", "Mhmm...", "I guess",
    "Sure, buddy", "No!", "No..?", "Nah", "Nope",
    "Probably not..", "y tho", "I don't care..",
    "Maybe", "Is this a trick question?", "bruh",
    "Perhaps", "Mhm", "Yuppers", "Yaaas", "Nu",
    "Nuh uh", "You don't wanna know", "Suuuuuure",
    "How would I know", "Probably", "Sure", "idk",
    "Sure, I guess", "Why not"
]

moo_answers = [
    "moo", "moo moo", "moooooo", "milk me", "moo!",
    "moomoo", "am cow", "me is cow", "*cow noise*",
    "am make milk", "MOO", "MOOOOOOOOO", "moo?",
    "oink", "moo?", "I am a cow", "milk time"
]

hi_answers = [
    "Hi", "Hai", "Hi there!", "HIIII", "Hewwo",
    "Hey"
]

bye_answers = [
    "Bye", "Bai", "Byebye!", "BYYYEEE", "Baibai",
    "Goodbye"
]


@ldr.add(f"{bot_name}(,|) (are|am|is|will|should|can|have|was|were|does|did|may|do)", simple_pattern=True, hide_help=True)
async def ask_bot(event):
    if event.args:
        await event.reply(choice(yesno_answers))


@ldr.add(f"{bot_name}(,|) say hi", simple_pattern=True, hide_help=True)
@ldr.add(f"say hi(,|) {bot_name}", simple_pattern=True, hide_help=True)
async def say_hi(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await reply.reply(choice(hi_answers))
    else:
        await event.reply(choice(hi_answers))


@ldr.add(f"{bot_name}(,|) say bye", simple_pattern=True, hide_help=True)
@ldr.add(f"say bye(,|) {bot_name}", simple_pattern=True, hide_help=True)
async def say_bye(event):
    if event.is_reply:
        reply = await event.get_reply_message()
        await reply.reply(choice(bye_answers))
    else:
        await event.reply(choice(bye_answers))


@ldr.add(f"let the bodies hit the", simple_pattern=True, hide_help=True)
async def floor(event):
    if not event.args:
        await event.reply("FLOOOOOOOOOOOOOOOOOOR")


@ldr.add(f"(^| )moo( |$)", raw_pattern=True, hide_help=True)
async def moo(event):
    await event.reply(choice(moo_answers))
