from random import choice

from ubot import ldr

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


@ldr.add(f"{bot_name}(,|) (are|am|is|will|should|can|have|was|were|does|did|may|do)", simple_pattern=True, hide_help=True, fun=True)
async def ask_bot(event):
    if event.args:
        await event.reply(choice(yesno_answers))


@ldr.add("i('|)m", simple_pattern=True, hide_help=True, chance=15, fun=True)
async def im_botname(event):
    if event.args and " " not in event.args:
        await event.reply(f"Hi {event.args}, I'm {bot_name}!")


@ldr.add(f"{bot_name}(,|) say", simple_pattern=True, hide_help=True, fun=True)
async def say_something(event):
    if event.args:
        if event.is_reply:
            reply = await event.get_reply_message()
            await reply.reply(event.args)
        else:
            await event.respond(event.args)

        try:
            await event.delete()
        except:
            pass


@ldr.add(f"{bot_name}(,|) edit to", simple_pattern=True, hide_help=True, sudo=True, fun=True)
async def edit_message(event):
    if event.args:
        if event.is_reply:
            reply = await event.get_reply_message()

            try:
                await reply.edit(event.args)
                await event.delete()
            except:
                pass


@ldr.add("let the bodies hit the", simple_pattern=True, hide_help=True, fun=True)
async def floor(event):
    if not event.args:
        await event.reply("FLOOOOOOOOOOOOOOOOOOR")


@ldr.add("^bruh$", raw_pattern=True, hide_help=True, chance=15, fun=True)
async def bruh_moment(event):
    await event.reply("moment")


@ldr.add("^ayaya$", raw_pattern=True, hide_help=True, fun=True)
async def ayaya(event):
    await event.reply("AYAYA")


@ldr.add("bab", hide_help=True, fun=True)
async def bab(event):
    if event.is_reply:
        await (await event.get_reply_message()).reply("You've been babbed!")
    else:
        await event.reply("Who am I supposed to bab?")


@ldr.add("unbab", hide_help=True, fun=True)
async def unbab(event):
    if event.is_reply:
        await (await event.get_reply_message()).reply("You've been unbabbed!")
    else:
        await event.reply("Who am I supposed to unbab?")


@ldr.add("(^| )moo( |$)", raw_pattern=True, hide_help=True, chance=25, fun=True)
async def moo(event):
    await event.reply(choice(moo_answers))


@ldr.add("kickme")
async def kickme(event):
    await event.reply("LOLE")

    try:
        await event.client.kick_participant(event.chat, await event.get_sender())
    except:
        pass
