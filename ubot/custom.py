from telethon.events.newmessage import NewMessage
from telethon.tl.types import (DocumentAttributeFilename,
                               DocumentAttributeImageSize,
                               DocumentAttributeSticker)


class ExtendedEvent(NewMessage.Event):
    async def get_text(self, return_msg=False, default=""):
        if self.args:
            if return_msg:
                return self.args, await self.get_reply_message() if self.is_reply else self.args, self

            return self.args

        if self.is_reply:
            reply = await self.get_reply_message()
            return reply.raw_text, reply if return_msg else reply.raw_text

        return default, self if return_msg else default

    async def get_image(self, with_reply=True):
        if self and self.media:
            if self.photo:
                return self.photo

            if self.document:
                if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in self.media.document.attributes:
                    return

                if self.gif or self.video or self.audio or self.voice:
                    return

                return self.media.document

        if with_reply and self.is_reply:
            return await (await self.get_reply_message()).get_image(with_reply=False)

    async def get_sticker(self):
        reply = await self.get_reply_message()

        if reply and reply.sticker:
            stick_attr = [i.alt for i in reply.sticker.attributes if isinstance(i, DocumentAttributeSticker)]
            size_attr = [i for i in reply.sticker.attributes if isinstance(i, DocumentAttributeImageSize)]

            if stick_attr and stick_attr[0]:
                return reply.sticker

            if size_attr and ((size_attr[0].w == 512 and size_attr[0].h <= 512) or (size_attr[0].w <= 512 and size_attr[0].h == 512)):
                return reply.sticker
