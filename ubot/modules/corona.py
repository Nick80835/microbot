# SPDX-License-Identifier: GPL-2.0-or-later

from requests import get

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="corona")
async def corona(event):
    text_arg = event.pattern_match.group(1)

    if text_arg:
        with get(f"https://corona.lmao.ninja/countries/{text_arg}") as response:
            if response.status_code == 200:
                response = response.json()
            else:
                await event.edit(f"`An error occurred, response code: `**{response.status}**")
                return

        response_text = f"`Stats for `**{response['country']}**\n\n`Cases: `**{response['cases']}**\n`Deaths: `**{response['deaths']}**\n`Recoveries: `**{response['recovered']}**"
        await event.edit(response_text)
    else:
        corona_data = get("https://corona.lmao.ninja/all").json()
        response_text = f"`Global stats`\n\n`Cases: `**{corona_data['cases']}**\n`Deaths: `**{corona_data['deaths']}**\n`Recoveries: `**{corona_data['recovered']}**"
        await event.edit(response_text)
