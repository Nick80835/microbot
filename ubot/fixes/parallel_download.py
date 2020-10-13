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

    async def download_chunk(self, chunk_start: int, chunk_end: int, chunk_number: int) -> str:
        async with self.aioclient.get(self.url, headers={"Range": f"bytes={chunk_start}-{chunk_end}"}) as response:
            async with aiofiles.open(f"ubot/cache/{self.file_name}.part{chunk_number}", mode="wb") as cache_file:
                while True:
                    chunk = await response.content.read(4096)

                    if not chunk:
                        break

                    await cache_file.write(chunk)

                await cache_file.flush()

        return f"ubot/cache/{self.file_name}.part{chunk_number}"

    async def generate_chunk_coros(self, content_length: int, chunk_size: int) -> list:
        place = 0
        chunk_number = 0
        chunk_coros = []

        while place < content_length:
            if place + chunk_size >= content_length:
                chunk_coros.append(self.download_chunk(place, content_length, chunk_number))
                break

            chunk_coros.append(self.download_chunk(place, place + chunk_size, chunk_number))

            place += chunk_size + 1
            chunk_number += 1

        return chunk_coros

    async def get_download_info(self, threads) -> (int, int, str):
        async with self.aioclient.get(self.url) as response:
            content_length = int(response.headers["content-length"])
            file_extension = mimetypes.guess_extension(response.headers["content-type"])

        if threads:
            if not content_length % threads:
                chunk_size = content_length / threads
            else:
                chunk_size = content_length // (threads - 1)
        else:
            if content_length < 100000000:
                chunk_size = 35000000
            elif content_length < 500000000:
                chunk_size = 100000000
            else:
                chunk_size = 300000000

        return content_length, chunk_size, file_extension


async def download(url: str, file_name: str, aioclient: ClientSession = ClientSession(), threads: int = None) -> str:
    downloader = ParallelDownload(url, aioclient, file_name)
    content_length, chunk_size, file_extension = await downloader.get_download_info(threads)
    chunk_coros = await downloader.generate_chunk_coros(content_length, chunk_size)
    downloaded_part_files = await gather(*chunk_coros)

    async with aiofiles.open(f"ubot/cache/{file_name}{file_extension}", "wb") as final_fh:
        for part_file in downloaded_part_files:
            async with aiofiles.open(part_file, "rb") as part_fh:
                await final_fh.write(await part_fh.read())

            remove(part_file)

        await final_fh.flush()

    return f"ubot/cache/{file_name}{file_extension}"
