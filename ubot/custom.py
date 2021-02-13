from telethon.events.newmessage import NewMessage
from telethon.tl.types import (DocumentAttributeFilename,
                               DocumentAttributeImageSize,
                               DocumentAttributeSticker)


class ExtendedEvent(NewMessage.Event):
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
