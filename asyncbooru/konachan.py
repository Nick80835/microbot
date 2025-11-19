from logging import getLogger
from typing import List

from aiohttp import ClientSession

from .exceptions import ApiException

logger = getLogger(__name__)
api_url = "https://konachan.com/post.json"
sauce_base = "https://konachan.com/post/show/"

ratings = {
    ("safe", "s"): "s",
    ("questionable", "q"): "q",
    ("explicit", "e", "x"): "e"
}


class KonachanPost:
    def __init__(self, json: dict):
        self.json = json
        self.id: int = json.get("id")
        self.file_url: str = json.get("file_url")
        self.file_size: int = json.get("file_size")
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


class Konachan:
    def __init__(self, client: ClientSession = None):
        self.client = client or ClientSession()

    async def get_random_post(self, tags: str = "", rating: str = "") -> KonachanPost:
        post_json = await self.json_request(f"order:random {tags}", 1, rating)
        return KonachanPost(post_json[0]) if post_json else None

    async def get_random_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[KonachanPost]:
        post_json = await self.json_request(f"order:random {tags}", limit, rating)
        return [KonachanPost(json) for json in post_json] if post_json else None

    async def get_latest_post(self, tags: str = "", rating: str = "") -> KonachanPost:
        post_json = await self.json_request(tags, 1, rating)
        return KonachanPost(post_json[0]) if post_json else None

    async def get_latest_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[KonachanPost]:
        post_json = await self.json_request(tags, limit, rating)
        return [KonachanPost(json) for json in post_json] if post_json else None

    async def json_request(self, tags: str = "", limit: int = 30, rating: str = "") -> List[dict]:
        params = {"limit": limit,
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
