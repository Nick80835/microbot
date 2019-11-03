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

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader
db = micro_bot.database


@ldr.add(pattern="save")
async def savenote(event):
    notename, notecontent = await get_text_arg(event)
    await db.execute("create table if not exists Notes (notename TEXT, notecontent TEXT)")

    if not notename or not notecontent:
        await event.edit("`Provide both a note name and content to save!`")
        return

    await event.edit(f"`Saving to note `**{notename}**`…`")
    await db.execute(f"delete from Notes where notename = '{notename}'")
    await db.execute(f"insert or ignore into Notes(notename, notecontent) values ('{notename}', '{notecontent}')")
    await event.edit(f"`Successfully saved to note `**{notename}**`!`")


@ldr.add(pattern="get")
async def getnote(event):
    notename = event.pattern_match.group(1).replace(" ", "_")
    await db.execute("create table if not exists Notes (notename TEXT, notecontent TEXT)")

    if not notename:
        notetuplelist = await db.fetch_all("select notename from Notes")
        notelist = '\n'.join([item[0] for item in notetuplelist])

        if notelist:
            await event.edit(f"`Provide a note name to get its content, saved notes:`\n**{notelist}**")
            return
        else:
            await event.edit(f"`You haven't saved any notes!\nUse `**{micro_bot.settings.get_config('cmd_prefix') or '.'}save**` to save notes.`")
            return

    notecontent = await db.fetch_one(f"select notecontent from Notes where notename = '{notename}'")

    if notecontent:
        await event.edit(f"{notecontent[0]}")
    else:
        await event.edit(f"`Note `**{notename}**` not found!`")


@ldr.add(incoming=True, noprefix=True, pattern="#(.*)")
async def getnoteincoming(event):
    if not micro_bot.settings.get_bool("incoming_allowed"):
        return

    notename = event.pattern_match.group(0).replace(" ", "_").lstrip("#")
    await db.execute("create table if not exists Notes (notename TEXT, notecontent TEXT)")

    if not notename:
        notetuplelist = await db.fetch_all("select notename from Notes")
        notelist = []

        for item in notetuplelist:
            notelist.append(item[0])

        notelist = '\n'.join(notelist)

        if notelist:
            await event.reply(f"`Provide a note name to get its content, saved notes:`\n**{notelist}**")
            return

    notecontent = await db.fetch_one(f"select notecontent from Notes where notename = '{notename}'")

    if notecontent:
        await event.reply(f"{notecontent[0]}")
    else:
        notetuplelist = await db.fetch_all("select notename from Notes")
        notelist = '\n'.join([item[0] for item in notetuplelist])
        await event.reply(f"`Note `**{notename}**` not found, saved notes:`\n**{notelist}**")


@ldr.add(pattern="del")
async def delnote(event):
    notename = event.pattern_match.group(1).replace(" ", "_")
    await db.execute("create table if not exists Notes (notename TEXT, notecontent TEXT)")

    if not notename:
        await event.edit("`I need a notes name to delete it!`")
        return

    await db.execute(f"delete from Notes where notename = '{notename}'")
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
