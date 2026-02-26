import logging
from typing import Any

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

KIPRIS_BASE_URL = "http://plus.kipris.or.kr/openapi/rest/v1/published"


def parse_kipris_patents(data: dict[str, Any]) -> list[dict[str, str]]:
    try:
        items = data["response"]["body"]["items"]["item"]
        if not items:
            return []
        if isinstance(items, dict):
            items = [items]
        return [
            {
                "title": item.get("inventionTitle", ""),
                "abstract": item.get("astrtCont", ""),
                "application_number": item.get("applicationNumber", ""),
            }
            for item in items
        ]
    except (KeyError, TypeError) as e:
        logger.warning(f"Failed to parse KIPRISplus response: {e}")
        return []


class KIPRISClient:
    def __init__(self, settings: Settings):
        self.api_key = settings.KIPRIS_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search_patents(
        self, keyword: str, num_of_rows: int = 50, page_no: int = 1
    ) -> list[dict[str, str]]:
        params = {
            "word": keyword,
            "numOfRows": num_of_rows,
            "pageNo": page_no,
            "ServiceKey": self.api_key,
        }
        try:
            response = await self.client.get(KIPRIS_BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return parse_kipris_patents(data)
        except httpx.HTTPError as e:
            logger.error(f"KIPRISplus API request failed: {e}")
            return []

    async def close(self):
        await self.client.aclose()
