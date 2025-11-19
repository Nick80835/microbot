from logging import getLogger
from typing import List

from aiohttp import ClientSession

from .exceptions import ApiException

logger = getLogger(__name__)
api_url = "https://capi-v2.sankakucomplex.com/posts/keyset"
sauce_base = "https://beta.sankakucomplex.com/post/show/"

ratings = {
    ("safe", "s"): "s",
    ("questionable", "q"): "q",
    ("explicit", "e", "x"): "e"
}


class SankakuPost:
    def __init__(self, json: dict):
        self.json = json
        self.id: int = json.get("id")
        self.file_url: str = json.get("file_url")
        self.file_size: int = json.get("file_size")
        self.file_type: str = json.get("file_type")
        self.rating: str = json.get("rating")
        self.height: int = json.get("height")
        self.width: int = json.get("width")
        self.md5: str = json.get("md5")
        self.tags: list = json.get("tags")
        self.total_score: int = json.get("total_score")
        self.source: str = json.get("source")
        self.author: dict = json.get("author")
        self.created_at: dict = json.get("created_at")
        self.parent_id: int = json.get("parent_id")
        self.sauce: str = sauce_base + str(self.id)


class Sankaku:
    def __init__(self, client: ClientSession = None):
        self.client = client or ClientSession()

    async def get_random_post(self, tags: str = "", rating: str = "") -> SankakuPost:
        post_json = await self.json_request(f"order:random {tags}", 1, rating)
        return SankakuPost(post_json[0]) if post_json else None

    async def get_random_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[SankakuPost]:
        post_json = await self.json_request(f"order:random {tags}", limit, rating)
        return [SankakuPost(json) for json in post_json] if post_json else None

    async def get_latest_post(self, tags: str = "", rating: str = "") -> SankakuPost:
        post_json = await self.json_request(tags, 1, rating)
        return SankakuPost(post_json[0]) if post_json else None

    async def get_latest_posts(self, tags: str = "", limit: int = 30, rating: str = "") -> List[SankakuPost]:
        post_json = await self.json_request(tags, limit, rating)
        return [SankakuPost(json) for json in post_json] if post_json else None

    async def json_request(self, tags: str = "", limit: int = 30, rating: str = "") -> List[dict]:
        params = {"limit": limit,
                  "page": 1,
                  "tags": f"{'rating:' + self._get_rating(rating) if rating else ''} {tags}".strip()}

        logger.debug("Handling request for tags: %s", params.get('tags'))

        async with self.client.get(api_url, params=params) as response:
            if response.status == 200:
                return (await response.json()).get("data")

            raise ApiException(f"Expected status 200, got {response.status}")

    @staticmethod
    def _get_rating(rating: str) -> str:
        rating_res = [v for k, v in ratings.items() if rating.lower() in k]
        return rating_res[0] if rating_res else ""
