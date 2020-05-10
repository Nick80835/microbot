# SPDX-License-Identifier: GPL-2.0-or-later

from ubot.micro_bot import micro_bot

ldr = micro_bot.loader


@ldr.add("corona")
async def corona(event):
    if event.args:
        async with ldr.aioclient.get(f"https://corona.lmao.ninja/v2/countries/{event.args}") as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.edit(f"`An error occurred, response code: `**{response.status}**")
                return

        response_text = f"`Stats for `**{response['country']}**\n\n`Cases: `**{response['cases']}** **({response['todayCases']} today)**\n`Deaths: `**{response['deaths']}** **({response['todayDeaths']} today)**\n`Recoveries: `**{response['recovered']}**"
        await event.edit(response_text)
    else:
        async with ldr.aioclient.get(f"https://corona.lmao.ninja/v2/all") as response:
            if response.status == 200:
                response = await response.json()
            else:
                await event.edit(f"`An error occurred, response code: `**{response.status}**")
                return

        response_text = f"`Global stats`\n\n`Cases: `**{response['cases']}** **({response['todayCases']} today)**\n`Deaths: `**{response['deaths']}** **({response['todayDeaths']} today)**\n`Recoveries: `**{response['recovered']}**"
        await event.edit(response_text)
