# SPDX-License-Identifier: GPL-2.0-or-later

from requests import get

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add(pattern="corona")
async def corona(event):
    if event.args:
        with get(f"https://corona.lmao.ninja/v2/countries/{event.args}") as response:
            if response.status_code == 200:
                response = response.json()
            else:
                await event.reply(f"`An error occurred, response code: `**{response.status}**")
                return

        response_text = f"`Stats for `**{response['country']}**\n\n`Cases: `**{response['cases']}** **({response['todayCases']} today)**\n`Deaths: `**{response['deaths']}** **({response['todayDeaths']} today)**\n`Recoveries: `**{response['recovered']}**"
        await event.reply(response_text)
    else:
        response = get("https://corona.lmao.ninja/v2/all").json()
        response_text = f"`Global stats`\n\n`Cases: `**{response['cases']}** **({response['todayCases']} today)**\n`Deaths: `**{response['deaths']}** **({response['todayDeaths']} today)**\n`Recoveries: `**{response['recovered']}**"
        await event.reply(response_text)
