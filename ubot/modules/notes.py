# SPDX-License-Identifier: GPL-2.0-or-later

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader
db = micro_bot.database

note_columns = ["notename", "notecontent"]


@ldr.add(pattern="save")
async def savenote(event):
    notename, notecontent = await get_text_arg(event)

    if not notename or not notecontent:
        await event.edit("`Provide both a note name and content to save!`")
        return

    await event.edit(f"`Saving to note `**{notename}**`…`")
    await db.single_row_write("Notes", note_columns, notename, notecontent)
    await event.edit(f"`Successfully saved to note `**{notename}**`!`")


@ldr.add(pattern="get")
async def getnote(event):
    notename = event.pattern_match.group(1).replace(" ", "_")

    if not notename:
        notelist = '\n'.join(await db.single_column_readall("Notes", note_columns, "notename"))

        if notelist:
            await event.edit(f"`Provide a note name to get its content, saved notes:`\n**{notelist}**")
            return
        else:
            await event.edit(f"`You haven't saved any notes!\nUse `**{micro_bot.settings.get_config('cmd_prefix') or '.'}save**` to save notes.`")
            return

    notecontent = await db.single_row_read("Notes", note_columns, notename)

    if notecontent:
        await event.edit(f"{notecontent}")
    else:
        notelist = '\n'.join(await db.single_column_readall("Notes", note_columns, "notename"))

        if notelist:
            await event.edit(f"`Note `**{notename}**` not found, saved notes:`\n**{notelist}**")
        else:
            await event.edit(f"`You haven't saved any notes!\nUse `**{micro_bot.settings.get_config('cmd_prefix') or '.'}save**` to save notes.`")


@ldr.add(incoming=True, noprefix=True, pattern="#(.*)")
async def getnoteincoming(event):
    if not micro_bot.settings.get_bool("incoming_allowed"):
        return

    notename = event.pattern_match.group(0).replace(" ", "_").lstrip("#")

    if not notename:
        notelist = '\n'.join(await db.single_column_readall("Notes", note_columns, "notename"))

        if notelist:
            await event.reply(f"`Provide a note name to get its content, saved notes:`\n**{notelist}**")
            return
        else:
            await event.reply(f"`There aren't any saved notes!`")
            return

    notecontent = await db.single_row_read("Notes", note_columns, notename)

    if notecontent:
        await event.reply(f"{notecontent}")
    else:
        notelist = '\n'.join(await db.single_column_readall("Notes", note_columns, "notename"))

        if notelist:
            await event.reply(f"`Note `**{notename}**` not found, saved notes:`\n**{notelist}**")
        else:
            await event.reply(f"`There aren't any saved notes!`")


@ldr.add(pattern="del")
async def delnote(event):
    notename = event.pattern_match.group(1).replace(" ", "_")

    if not notename:
        await event.edit("`I need a notes name to delete it!`")
        return

    await db.single_row_delete("Notes", note_columns, notename)
    await event.edit(f"`Note `**{notename}**` successfully deleted!`")


async def get_text_arg(event):
    text_arg = event.pattern_match.group(1)
    notename = None
    notecontent = None

    if event.is_reply and text_arg:
        reply = await event.get_reply_message()
        notename = text_arg.replace(" ", "_")
        notecontent = reply.text
    elif text_arg:
        notename = text_arg.split(" ")[0]
        notecontent = " ".join(text_arg.split(" ")[1:])

    return notename, notecontent
