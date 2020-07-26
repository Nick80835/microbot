# SPDX-License-Identifier: GPL-2.0-or-later

import mimetypes
from asyncio import gather
from os import remove

import aiofiles
from aiohttp import ClientSession


class ParallelDownload:
    def __init__(self, url: str, aioclient: ClientSession, file_name: str):
        self.url = url
        self.aioclient = aioclient
        self.file_name = file_name

    async def download_chunk(self, chunk_start: int, chunk_end: int, total_size: int, chunk_number: int) -> str:
        chunk_headers = {
            "Content-Range": f"bytes {chunk_start}-{chunk_end}/{total_size}"
        }

        async with self.aioclient.get(self.url, headers=chunk_headers) as response:
            async with aiofiles.open(f"ubot/cache/{self.file_name}.part{chunk_number}", mode="wb") as cache_file:
                while True:
                    chunk = await response.content.read(4096)

                    if not chunk:
                        break

                    await cache_file.write(chunk)

                await cache_file.flush()

        return f"ubot/cache/{self.file_name}.part{chunk_number}"

    async def generate_chunk_coros(self, chunk_size: int) -> (list, str):
        async with self.aioclient.get(self.url) as response:
            content_length = int(response.headers["content-length"])
            file_extension = mimetypes.guess_extension(response.headers["content-type"])

        place = 0
        chunk_number = 0
        chunk_coros = []

        while place < content_length:
            if place + chunk_size > content_length:
                chunk_coros.append(self.download_chunk(place, content_length, content_length, chunk_number))
                break

            chunk_coros.append(self.download_chunk(place, place + chunk_size, content_length, chunk_number))
            place += chunk_size

            chunk_number += 1

        return chunk_coros, file_extension


async def download(url: str, file_name: str, aioclient: ClientSession = ClientSession(), chunk_size: int = 15000000) -> str:
    downloader = ParallelDownload(url, aioclient, file_name)
    chunk_coros, file_extension = await downloader.generate_chunk_coros(chunk_size)
    downloaded_part_files = await gather(*chunk_coros)

    async with aiofiles.open(f"ubot/cache/{file_name}{file_extension}", "wb") as final_fh:
        for part_file in downloaded_part_files:
            async with aiofiles.open(part_file, "rb") as part_fh:
                await final_fh.write(await part_fh.read())

            remove(part_file)

        await final_fh.flush()

    return f"ubot/cache/{file_name}{file_extension}"
