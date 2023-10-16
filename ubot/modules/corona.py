# SPDX-License-Identifier: GPL-2.0-or-later

from requests import get

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="corona")
async def corona(event):
    text_arg = event.pattern_match.group(1)

    if text_arg:
        with get(f"https://corona.lmao.ninja/v2/countries/{text_arg}") as response:
            if response.status_code == 200:
                response = response.json()
            else:
                await event.edit(f"`An error occurred, response code: `**{response.status}**")
                return

        response_text = f"`Stats for `**{response['country']}**\n\n`Cases: `**{response['cases']}** **({response['todayCases']} today)**\n`Deaths: `**{response['deaths']}** **({response['todayDeaths']} today)**\n`Recoveries: `**{response['recovered']}**"
        await event.edit(response_text)
    else:
        response = get("https://corona.lmao.ninja/v2/all").json()
        response_text = f"`Global stats`\n\n`Cases: `**{response['cases']}** **({response['todayCases']} today)**\n`Deaths: `**{response['deaths']}** **({response['todayDeaths']} today)**\n`Recoveries: `**{response['recovered']}**"
        await event.edit(response_text)
