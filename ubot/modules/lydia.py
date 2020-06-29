# SPDX-License-Identifier: GPL-2.0-or-later

from functools import partial

from coffeehouse import LydiaAI

from ubot.micro_bot import ldr

bot_name = ldr.settings.get_config("bot_name") or "bot"

if ldr.settings.get_config("lydia_key"):
    lydia_ai = LydiaAI(ldr.settings.get_config("lydia_key"))
    session = lydia_ai.create_session("en")

    @ldr.add(f"{bot_name}(,|)", simple_pattern=True, hide_help=True)
    async def talk_to_lydia(event):
        if event.args:
            thought_text = await event.client.loop.run_in_executor(ldr.thread_pool, partial(async_think, event.args))
            await event.reply(thought_text)

    def async_think(text):
        return_text = session.think_thought(text)
        return return_text
