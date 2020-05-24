# SPDX-License-Identifier: GPL-2.0-or-later

from howdoi import howdoi

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add("hdi")
async def howdoi_cmd(event):
    response = howdoi.howdoi(vars(howdoi.get_parser().parse_args(event.args.split(' '))))
    await event.reply(f"**Query:**\n`{event.args}`\n**Answer:**\n`{response}`")
