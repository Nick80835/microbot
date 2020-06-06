# SPDX-License-Identifier: GPL-2.0-or-later

import os
import re

from howdoi import howdoi

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader
os.environ["HOWDOI_SEARCH_ENGINE"] = "bing"


@ldr.add("hdi")
async def howdoi_cmd(event):
    if not event.args:
        await event.reply(f"Syntax: {ldr.settings.get_config('cmd_prefix') or '.'}hdi <question>")
        return

    response = howdoi.howdoi(vars(howdoi.get_parser().parse_args(event.args.split(' '))))
    response = re.sub(r'\n\n+', '\n\n', response).strip()

    await event.reply(f"**Query:**\n{event.args}\n**Answer:**\n{response}")
