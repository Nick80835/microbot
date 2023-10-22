from re import Match
from typing import Any

from telethon.events.callbackquery import CallbackQuery
from telethon.events.inlinequery import InlineQuery
from telethon.events.newmessage import NewMessage
from telethon.tl.types import (DocumentAttributeFilename,
                               DocumentAttributeImageSize,
                               DocumentAttributeSticker,
                               MessageEntityMentionName)

from ubot.command import (CallbackQueryCommand, Command, InlineArticleCommand,
                          InlinePhotoCommand)
from ubot.database import ChatWrapper


class ExtendedNewMessage(NewMessage.Event):
    pattern_match: Match[str] # pattern match as returned by re.search when it's used in the command handler
    chat_db: ChatWrapper # database reference for the chat this command was executed in
    object: Command # the object constructed when the command associated with this event was added
    command: str # the base command with no prefix, no args and no other_args; the whole pattern if raw_pattern is used
    prefix: str # prefix used to call this command, such as "/" or "g."; not set if simple_pattern/raw_pattern is used
    extra: Any # any object you set to extra when registering the command associated with this event
    args: str # anything after the command itself and any groups caught in other_args, such as booru tags
    other_args: tuple # any groups between the args group and the command itself
    nsfw_disabled: bool # only set if pass_nsfw is True; this value is the opposite of nsfw_enabled in chat_db

    @property
    def has_user_entities(self) -> bool:
        return any([i for i in self.entities if isinstance(i, MessageEntityMentionName)]) if self.entities else False

    async def get_text(self, return_msg=False, default=""):
        if self.args:
            if return_msg:
                return (self.args, await self.get_reply_message()) if self.is_reply else (self.args, self)

            return self.args

        if self.is_reply:
            reply = await self.get_reply_message()
            return (reply.raw_text, reply) if return_msg else reply.raw_text

        return (default, self) if return_msg else default

    async def get_image(self, event=None, with_reply=True, force_reply=False):
        event = event or self

        if event and event.media and not force_reply:
            if event.photo:
                return event.photo

            if event.document:
                if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in event.media.document.attributes:
                    return

                if event.gif or event.video or event.audio or event.voice:
                    return

                return event.media.document

        if with_reply and event.is_reply:
            return await event.get_image(event=await event.get_reply_message(), with_reply=False)

    async def get_sticker(self):
        reply = await self.get_reply_message()

        if reply and reply.sticker:
            stick_attr = [i.alt for i in reply.sticker.attributes if isinstance(i, DocumentAttributeSticker)]
            size_attr = [i for i in reply.sticker.attributes if isinstance(i, DocumentAttributeImageSize)]

            if stick_attr and stick_attr[0]:
                return reply.sticker

            if size_attr and ((size_attr[0].w == 512 and size_attr[0].h <= 512) or (size_attr[0].w <= 512 and size_attr[0].h == 512)):
                return reply.sticker

    async def respond(self, *args, **kwargs):
        if self.reply_to and self.reply_to.forum_topic and not kwargs.get("reply_to", None):
            if self.reply_to.reply_to_top_id:
                return await self.message.respond(*args, **kwargs|{"reply_to": self.reply_to.reply_to_top_id})
            elif self.reply_to.reply_to_msg_id:
                return await self.message.respond(*args, **kwargs|{"reply_to": self.reply_to.reply_to_msg_id})

        return await self.message.respond(*args, **kwargs)


class ExtendedCallbackQuery(CallbackQuery.Event):
    chat_db: ChatWrapper|None
    object: CallbackQueryCommand
    command: str
    extra: Any
    args: str


class ExtendedInlineQuery(InlineQuery.Event):
    pattern_match: Match[str]
    parse_mode: str
    object: InlineArticleCommand|InlinePhotoCommand
    command: str
    extra: Any
    args: str
    other_args: tuple
    nsfw_disabled: bool
    link_preview: bool
