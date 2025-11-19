from logging import getLogger
from typing import List

from aiohttp import ClientSession

from .exceptions import ApiException

logger = getLogger(__name__)
api_url = "https://yande.re/post.json"
sauce_base = "https://yande.re/post/show/"

ratings = {
    ("safe", "s"): "s",
    ("questionable", "q"): "q",
    ("explicit", "e", "x"): "e"
}


class YanderePost:
    def __init__(self, json: dict):
        self.json = json
        self.id: int = json.get("id")
        self.file_url: str = json.get("file_url")
        self.file_size: int = json.get("file_size")
        self.file_ext: str = json.get("file_ext")
        self.rating: str = json.get("rating")
        self.height: int = json.get("height")
        self.width: int = json.get("width")
        self.md5: str = json.get("md5")
        self.tags: str = json.get("tags")
        self.score: int = json.get("score")
        self.source: str = json.get("source")
        self.creator_id: int = json.get("creator_id")
        self.created_at: int = json.get("created_at")
        self.parent_id: int = json.get("parent_id")
        self.sauce: str = sauce_base + str(self.id)


class Yandere:
    def __init__(self, client: ClientSession = None):
        self.client = client or ClientSession()

    async def get_random_post(self, tags: str = "", rating: str = "") -> YanderePost:
        post_json = await self.json_request(f"order:random {tags}", 1, rating)
        return YanderePost(post_json[0]) if post_json else None

    async def get_random_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[YanderePost]:
        post_json = await self.json_request(f"order:random {tags}", limit, rating)
        return [YanderePost(json) for json in post_json] if post_json else None

    async def get_latest_post(self, tags: str = "", rating: str = "") -> YanderePost:
        post_json = await self.json_request(tags, 1, rating)
        return YanderePost(post_json[0]) if post_json else None

    async def get_latest_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[YanderePost]:
        post_json = await self.json_request(tags, limit, rating)
        return [YanderePost(json) for json in post_json] if post_json else None

    async def json_request(self, tags: str = "", limit: int = 30, rating: str = "") -> List[dict]:
        params = {"limit": limit,
                  "page": 1,
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
