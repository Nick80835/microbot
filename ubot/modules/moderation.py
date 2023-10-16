from telethon.errors import UserAdminInvalidError

from ubot import ldr
from ubot.fixes.utils import get_user


@ldr.add("kick", moderation=True)
async def kick_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't kick users in this chat.")
        return

    user_to_kick = await get_user(event, allow_channel=True)

    try:
        if user_to_kick:
            admin_perms = await event.client.get_permissions(event.chat, event.sender)
            target_perms = await event.client.get_permissions(event.chat, user_to_kick)

            if target_perms.is_admin:
                await event.reply("I won't kick an admin.")
                return

            if not admin_perms.ban_users:
                await event.reply("You don't have the rights to kick users.")
                return

            await event.client.edit_permissions(event.chat, user_to_kick, view_messages=False)
            await event.client.edit_permissions(event.chat, user_to_kick, view_messages=True)
            await event.reply(f"Successfully kicked {user_to_kick.id}!")
    except UserAdminInvalidError:
        await event.reply("I can't kick them!")


@ldr.add("ban", moderation=True)
async def ban_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't ban users in this chat.")
        return

    user_to_ban = await get_user(event, allow_channel=True)

    try:
        if user_to_ban:
            admin_perms = await event.client.get_permissions(event.chat, event.sender)
            target_perms = await event.client.get_permissions(event.chat, user_to_ban)

            if target_perms.is_admin:
                await event.reply("I won't ban an admin.")
                return

            if not admin_perms.ban_users:
                await event.reply("You don't have the rights to ban users.")
                return

            await event.client.edit_permissions(event.chat, user_to_ban, view_messages=False)
            await event.reply(f"Successfully banned {user_to_ban.id}!")
    except UserAdminInvalidError:
        await event.reply("I can't ban them!")

