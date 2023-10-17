from datetime import timedelta

from telethon.tl.types import Channel, Chat, MessageEntityMentionName


async def get_user(event, allow_channel=False):
    if mention_entities := [i for i in event.get_entities_text() if isinstance(i, MessageEntityMentionName)]:
        if len(mention_entities) > 1:
            await event.reply("You provided too many arguments!")
            return

        try:
            user = await event.client.get_input_entity(mention_entities[0].user_id)

            if isinstance(user, Chat) or (isinstance(user, Channel) and not allow_channel):
                raise TypeError

            return user
        except (ValueError, TypeError):
            await event.reply("There was an error getting the user's ID!")
    elif event.args:
        if event.args.isnumeric():
            user_id = int(event.args)
        else:
            user_id = None

        try:
            user = await event.client.get_input_entity(user_id or event.args)

            if isinstance(user, Chat) or (isinstance(user, Channel) and not allow_channel):
                raise TypeError

            return user
        except (ValueError, TypeError):
            await event.reply("The ID or username you provided was invalid!")
    elif event.is_reply:
        reply = await event.get_reply_message()

        if reply and reply.sender_id:
            try:
                user = await event.client.get_input_entity(reply.sender_id)

                if isinstance(user, Chat) or (isinstance(user, Channel) and not allow_channel):
                    raise TypeError

                return user
            except (ValueError, TypeError):
                await event.reply("There was an error getting the user's ID!")
                return
        else:
            await event.reply("Give me a user ID, username or reply!")
            return
    else:
        await event.reply("Give me a user ID, username or reply!")


def parse_time(time_num: int, unit: str) -> timedelta:
    match unit:
        case "m":
            return timedelta(seconds=time_num * 60)
        case "h":
            return timedelta(seconds=time_num * 60 * 60)
        case "d":
            return timedelta(seconds=time_num * 24 * 60 * 60)
