import mimetypes
import os

import aiofiles


class Cache():
    if not os.path.exists("ubot/cache"):
        os.mkdir("ubot/cache")

    def __init__(self, aioclient):
        self.aioclient = aioclient

    async def cache_file(self, url: str, filename: str):
        async with self.aioclient.get(url) as response:
            file_extension = mimetypes.guess_extension(response.headers["content-type"])

            async with aiofiles.open(f"ubot/cache/{filename}{file_extension}", mode="wb") as cache_file:
                while True:
                    chunk = await response.content.read(4096)

                    if not chunk:
                        break

                    await cache_file.write(chunk)

            return f"ubot/cache/{filename}{file_extension}"

    def remove_cache(self, filename: str):
        os.remove(filename)

    async def is_cache_required(self, url: str) -> (bool, int):
        async with self.aioclient.get(url) as response:
            size = int(response.headers["content-length"])
            return size >= 20000000, size
