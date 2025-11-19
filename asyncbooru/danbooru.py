from logging import getLogger
from typing import List

from aiohttp import ClientSession

from .exceptions import ApiException

logger = getLogger(__name__)
api_url = "http://danbooru.donmai.us/posts.json"
sauce_base = "https://danbooru.donmai.us/posts/"

ratings = {
    ("safe", "s"): "s",
    ("questionable", "q"): "q",
    ("explicit", "e", "x"): "e"
}


class DanbooruPost:
    def __init__(self, json: dict):
        self.json = json
        self.id: int = json.get("id")
        self.file_url: str = json.get("file_url")
        self.large_file_url: str = json.get("large_file_url")
        self.file_size: int = json.get("file_size")
        self.file_ext: str = json.get("file_ext")
        self.rating: str = json.get("rating")
        self.image_height: int = json.get("image_height")
        self.image_width: int = json.get("image_width")
        self.md5: str = json.get("md5")
        self.tags: str = json.get("tag_string")
        self.score: int = json.get("score")
        self.source: str = json.get("source")
        self.uploader_id: int = json.get("uploader_id")
        self.created_at: str = json.get("created_at")
        self.parent_id: int = json.get("parent_id")
        self.sauce: str = sauce_base + str(self.id)


class Danbooru:
    def __init__(self, client: ClientSession = None):
        self.client = client or ClientSession()

    async def get_random_post(self, tags: str = "", rating: str = "") -> DanbooruPost:
        post_json = await self.json_request(tags, 1, rating, True)
        return DanbooruPost(post_json[0]) if post_json else None

    async def get_random_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[DanbooruPost]:
        post_json = await self.json_request(tags, limit, rating, True)
        return [DanbooruPost(json) for json in post_json] if post_json else None

    async def get_latest_post(self, tags: str = "", rating: str = "") -> DanbooruPost:
        post_json = await self.json_request(tags, 1, rating)
        return DanbooruPost(post_json[0]) if post_json else None

    async def get_latest_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[DanbooruPost]:
        post_json = await self.json_request(tags, limit, rating)
        return [DanbooruPost(json) for json in post_json] if post_json else None

    async def json_request(self, tags: str = "", limit: int = 30, rating: str = "", random: bool = False) -> List[dict]:
        params = {"limit": limit,
                  "random": str(random),
                  "tags": f"{'rating:' + self._get_rating(rating) if rating else ''} {tags}".strip()}

        logger.debug("Handling request for tags: %s", params.get('tags'))

        async with self.client.get(api_url, params=params) as response:
            if response.status == 200:
                return await response.json()

            raise ApiException(f"Expected status 200, got {response.status}")

    @staticmethod
    def _get_rating(rating: str) -> str:
        rating_res = [v for k, v in ratings.items() if rating.lower() in k]
        return rating_res[0] if rating_res else ""
