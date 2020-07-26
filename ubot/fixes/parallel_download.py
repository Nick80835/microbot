# SPDX-License-Identifier: GPL-2.0-or-later

import mimetypes
from asyncio import gather
from io import BytesIO

from aiohttp import ClientSession


class ParallelDownload:
    def __init__(self, url: str, aioclient: ClientSession):
        self.url = url
        self.aioclient = aioclient

    async def download_chunk(self, chunk_start: int, chunk_end: int, total_size: int) -> bytes:
        chunk_headers = {
            "Content-Range": f"bytes {chunk_start}-{chunk_end}/{total_size}"
        }

        async with self.aioclient.get(self.url, headers=chunk_headers) as response:
            chunk_data = await response.read()

        return chunk_data

    async def generate_chunk_coros(self, chunk_size: int = 1000000) -> list:
        async with self.aioclient.get(self.url) as response:
            content_length = int(response.headers["content-length"])
            file_extension = mimetypes.guess_extension(response.headers["content-type"])

        place = 0
        remaining_length = content_length
        chunk_coros = []

        while remaining_length > 0:
            if remaining_length < chunk_size:
                chunk_coros.append(self.download_chunk(place, content_length, content_length))
                break

            chunk_coros.append(self.download_chunk(place, place + chunk_size, content_length))
            place += chunk_size
            remaining_length -= chunk_size

        return chunk_coros, file_extension


async def download(url: str, aioclient: ClientSession = ClientSession()) -> BytesIO:
    downloader = ParallelDownload(url, aioclient)
    chunk_coros, file_extension = await downloader.generate_chunk_coros()
    downloaded_byte_chunks = await gather(*chunk_coros)
    downloaded_bytes = BytesIO(b''.join(downloaded_byte_chunks))
    downloaded_bytes.name = f"downloaded_file{file_extension}"

    return downloaded_bytes
