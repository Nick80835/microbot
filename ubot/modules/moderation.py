from datetime import datetime, timezone
from re import IGNORECASE, compile, sub

from telethon.errors import UserAdminInvalidError

from ubot import ldr
from ubot.fixes.utils import get_user, parse_time

time_regex = compile(r"(?:^| )(\d+)([mhd])$", IGNORECASE)


@ldr.add("kick", moderation=True, help="Kick a user.")
async def kick_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't kick users in this chat.")
        return

    user_to_kick = await get_user(event, allow_channel=True)

    try:
        if user_to_kick:
            if user_to_kick.id == ldr.micro_bot.me.id:
                await event.reply("I won't kick myself, baka.")
                return

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


@ldr.add("ban", moderation=True, help="Ban a user forever, or for a certain amount of time given at the end of the command like 30m, 12h or 5d.")
async def ban_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't ban users in this chat.")
        return

    if time_match := time_regex.search(event.args):
        event.args = time_regex.sub("", event.args).strip()

    user_to_ban = await get_user(event, allow_channel=True)

    try:
        if user_to_ban:
            if user_to_ban.id == ldr.micro_bot.me.id:
                await event.reply("I won't ban myself, baka.")
                return

            admin_perms = await event.client.get_permissions(event.chat, event.sender)
            target_perms = await event.client.get_permissions(event.chat, user_to_ban)

            if target_perms.is_admin:
                await event.reply("I won't ban an admin.")
                return

            if not admin_perms.ban_users:
                await event.reply("You don't have the rights to ban users.")
                return

            if time_match := time_regex.search(event.args):
                mute_length = parse_time(int(time_match.group(1)), time_match.group(2))
                await event.client.edit_permissions(event.chat, user_to_ban, view_messages=False, until_date=mute_length)
                await event.reply(f"Successfully banned {user_to_ban.id} until {(datetime.now(timezone.utc) + mute_length).strftime('%H:%M %b %d, %Y UTC')}!")
                return

            await event.client.edit_permissions(event.chat, user_to_ban, view_messages=False)
            await event.reply(f"Successfully banned {user_to_ban.id} for all of eternity!")
    except UserAdminInvalidError:
        await event.reply("I can't ban them!")


@ldr.add("unban", moderation=True, help="Unban a user.")
async def unban_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't unban users in this chat.")
        return

    user_to_unban = await get_user(event, allow_channel=True)

    try:
        if user_to_unban:
            admin_perms = await event.client.get_permissions(event.chat, event.sender)

            if not admin_perms.ban_users:
                await event.reply("You don't have the rights to unban users.")
                return

            await event.client.edit_permissions(event.chat, user_to_unban, view_messages=True)
            await event.reply(f"Successfully unbanned {user_to_unban.id}!")
    except UserAdminInvalidError:
        await event.reply("I can't unban them!")


@ldr.add("mute", moderation=True, help="Mute a user forever, or for a certain amount of time given at the end of the command like 30m, 12h or 5d.")
async def mute_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't mute users in this chat.")
        return

    if time_match := time_regex.search(event.args):
        event.args = time_regex.sub("", event.args).strip()

    user_to_mute = await get_user(event, allow_channel=True)

    try:
        if user_to_mute:
            if user_to_mute.id == ldr.micro_bot.me.id:
                await event.reply("I won't mute myself, baka.")
                return

            admin_perms = await event.client.get_permissions(event.chat, event.sender)
            target_perms = await event.client.get_permissions(event.chat, user_to_mute)

            if target_perms.is_admin:
                await event.reply("I won't mute an admin.")
                return

            if not admin_perms.ban_users:
                await event.reply("You don't have the rights to mute users.")
                return

            if time_match:
                mute_length = parse_time(int(time_match.group(1)), time_match.group(2))
                await event.client.edit_permissions(event.chat, user_to_mute, send_messages=False, until_date=mute_length)
                await event.reply(f"Successfully muted {user_to_mute.id} until {(datetime.now(timezone.utc) + mute_length).strftime('%H:%M %b %d, %Y UTC')}!")
                return

            await event.client.edit_permissions(event.chat, user_to_mute, send_messages=False)
            await event.reply(f"Successfully muted {user_to_mute.id} for all of eternity!")
    except UserAdminInvalidError:
        await event.reply("I can't mute them!")


@ldr.add("unmute", moderation=True, help="Unmute a user.")
async def unmute_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't unmute users in this chat.")
        return

    user_to_unmute = await get_user(event, allow_channel=True)

    try:
        if user_to_unmute:
            admin_perms = await event.client.get_permissions(event.chat, event.sender)

            if not admin_perms.ban_users:
                await event.reply("You don't have the rights to unmute users.")
                return

            await event.client.edit_permissions(event.chat, user_to_unmute, send_messages=True)
            await event.reply(f"Successfully unmuted {user_to_unmute.id}!")
    except UserAdminInvalidError:
        await event.reply("I can't unmute them!")
