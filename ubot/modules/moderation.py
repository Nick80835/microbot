from datetime import datetime, timezone
from re import IGNORECASE, compile

from telethon.errors import UserAdminInvalidError, UserNotParticipantError
from telethon.tl.types import InputPeerUser

from ubot import ldr
from ubot.fixes.utils import get_user, parse_time

bot_name = ldr.settings.get_config("bot_name") or "bot"
time_regex = compile(r"(?:^| )(?:for )?(\d+) ?(m(?:ins?|inutes?)?|h(?:rs?|ours?)?|d(?:ays?)?)$", IGNORECASE)


@ldr.add("kick", moderation=True, help="Kick a user.")
@ldr.add(f"{bot_name}(,|) kick", moderation=True, simple_pattern=True, hide_help=True)
async def kick_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't kick users in this chat.")
        return

    if time_regex.sub("", event.args).strip().lower() == "me" and not event.has_user_entities:
        self_harm = True
        user_to_kick = await event.get_sender()
    else:
        self_harm = False
        user_to_kick = await get_user(event, allow_channel=True)

    try:
        if user_to_kick:
            if isinstance(user_to_kick, InputPeerUser) and user_to_kick.user_id == ldr.micro_bot.me.id:
                await event.reply("I won't kick myself, baka.")
                return

            admin_perms = await event.client.get_permissions(event.chat, event.sender)

            try:
                target_perms = await event.client.get_permissions(event.chat, user_to_kick)
            except UserNotParticipantError:
                target_perms = None

            if target_perms and target_perms.is_admin:
                await event.reply("I won't kick an admin.")
                return

            if not admin_perms.ban_users and not self_harm:
                await event.reply("You don't have the rights to kick users.")
                return

            await event.client.edit_permissions(event.chat, user_to_kick, view_messages=False)
            await event.client.edit_permissions(event.chat, user_to_kick, view_messages=True)
            await event.reply("Cya!" if self_harm else f"Successfully kicked {user_to_kick.user_id if isinstance(user_to_kick, InputPeerUser) else user_to_kick.channel_id}!")
    except UserAdminInvalidError:
        await event.reply("I can't kick them!")


@ldr.add("ban", moderation=True, help="Ban a user forever, or for a certain amount of time given at the end of the command like 30m, 12h or 5d.")
@ldr.add(f"{bot_name}(,|) ban", moderation=True, simple_pattern=True, hide_help=True)
async def ban_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't ban users in this chat.")
        return

    if time_match := time_regex.search(event.args):
        event.args = time_regex.sub("", event.args).strip()

    if time_regex.sub("", event.args).strip().lower() == "me" and not event.has_user_entities:
        await event.reply("I don't think I should do that…")
        return

    user_to_ban = await get_user(event, allow_channel=True)

    try:
        if user_to_ban:
            if isinstance(user_to_ban, InputPeerUser) and user_to_ban.user_id == ldr.micro_bot.me.id:
                await event.reply("I won't ban myself, baka.")
                return

            admin_perms = await event.client.get_permissions(event.chat, event.sender)

            try:
                target_perms = await event.client.get_permissions(event.chat, user_to_ban)
            except UserNotParticipantError:
                target_perms = None

            if target_perms and target_perms.is_admin:
                await event.reply("I won't ban an admin.")
                return

            if not admin_perms.ban_users:
                await event.reply("You don't have the rights to ban users.")
                return

            if time_match:
                mute_length = parse_time(int(time_match.group(1)), time_match.group(2)[0])
                await event.client.edit_permissions(event.chat, user_to_ban, view_messages=False, until_date=mute_length)
                await event.reply(f"Successfully banned {user_to_ban.user_id if isinstance(user_to_ban, InputPeerUser) else user_to_ban.channel_id} until {(datetime.now(timezone.utc) + mute_length).strftime('%H:%M %b %d, %Y UTC')}!")
                return

            await event.client.edit_permissions(event.chat, user_to_ban, view_messages=False)
            await event.reply(f"Successfully banned {user_to_ban.user_id if isinstance(user_to_ban, InputPeerUser) else user_to_ban.channel_id} for all of eternity!")
    except UserAdminInvalidError:
        await event.reply("I can't ban them!")


@ldr.add("unban", moderation=True, help="Unban a user.")
@ldr.add(f"{bot_name}(,|) unban", moderation=True, simple_pattern=True, hide_help=True)
async def unban_user(event):
    if event.args.lower() == "me" and not event.has_user_entities:
        await event.reply("You probably aren't banned.")
        return

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
            await event.reply(f"Successfully unbanned {user_to_unban.user_id if isinstance(user_to_unban, InputPeerUser) else user_to_unban.channel_id}!")
    except UserAdminInvalidError:
        await event.reply("I can't unban them!")


@ldr.add("mute", moderation=True, help="Mute a user forever, or for a certain amount of time given at the end of the command like 30m, 12h or 5d.")
@ldr.add(f"{bot_name}(,|) mute", moderation=True, simple_pattern=True, hide_help=True)
async def mute_user(event):
    if not (await event.client.get_permissions(event.chat, "me")).ban_users:
        await event.reply("I can't mute users in this chat.")
        return

    if time_match := time_regex.search(event.args):
        event.args = time_regex.sub("", event.args).strip()

    if time_regex.sub("", event.args).strip().lower() == "me" and not event.has_user_entities:
        self_harm = True
        user_to_mute = await event.get_sender()
    else:
        self_harm = False
        user_to_mute = await get_user(event, allow_channel=True)

    try:
        if user_to_mute:
            if isinstance(user_to_mute, InputPeerUser) and user_to_mute.user_id == ldr.micro_bot.me.id:
                await event.reply("I won't mute myself, baka.")
                return

            admin_perms = await event.client.get_permissions(event.chat, event.sender)

            try:
                target_perms = await event.client.get_permissions(event.chat, user_to_mute)
            except UserNotParticipantError:
                target_perms = None

            if target_perms and target_perms.is_admin:
                await event.reply("I won't mute an admin.")
                return

            if not admin_perms.ban_users and not self_harm:
                await event.reply("You don't have the rights to mute users.")
                return

            if time_match:
                mute_length = parse_time(int(time_match.group(1)), time_match.group(2)[0])
                await event.client.edit_permissions(event.chat, user_to_mute, send_messages=False, until_date=mute_length)

                if self_harm:
                    await event.reply(f"Since you asked nicely, I've muted you until {(datetime.now(timezone.utc) + mute_length).strftime('%H:%M %b %d, %Y UTC')}!")
                else:
                    await event.reply(f"Successfully muted {user_to_mute.user_id if isinstance(user_to_mute, InputPeerUser) else user_to_mute.channel_id} until {(datetime.now(timezone.utc) + mute_length).strftime('%H:%M %b %d, %Y UTC')}!")

                return

            if self_harm:
                await event.reply("I don't think I should do that…")
            else:
                await event.client.edit_permissions(event.chat, user_to_mute, send_messages=False)
                await event.reply(f"Successfully muted {user_to_mute.user_id if isinstance(user_to_mute, InputPeerUser) else user_to_mute.channel_id} for all of eternity!")
    except UserAdminInvalidError:
        await event.reply("I can't mute them!")


@ldr.add("unmute", moderation=True, help="Unmute a user.")
@ldr.add(f"{bot_name}(,|) unmute", moderation=True, simple_pattern=True, hide_help=True)
async def unmute_user(event):
    if event.args.lower() == "me" and not event.has_user_entities:
        await event.reply("You probably aren't muted.")
        return

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
            await event.reply(f"Successfully unmuted {user_to_unmute.user_id if isinstance(user_to_unmute, InputPeerUser) else user_to_unmute.channel_id}!")
    except UserAdminInvalidError:
        await event.reply("I can't unmute them!")
