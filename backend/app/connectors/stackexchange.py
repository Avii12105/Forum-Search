import html
import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx

from app.connectors.base import BaseConnector
from app.schemas.document import ForumDocument, ForumType, ContentType

logger = logging.getLogger(__name__)

class StackExchangeConnector(BaseConnector):
    """
    Connector for Stack Exchange API (targeting Stack Overflow).
    API Docs: https://api.stackexchange.com/docs
    """
    
    def __init__(self, site: str = "stackoverflow"):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = site

    async def search(self, query: str, limit: int = 10) -> List[ForumDocument]:
        """
        Search Stack Overflow for questions matching the query.
        """
        url = f"{self.base_url}/search/advanced"
        params = {
            "order": "desc",
            "sort": "votes",
            "q": query,
            "site": self.site,
            "pagesize": limit,
            "filter": "withbody" # Requests the API to include the question body
        }

        documents = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Check for quota warnings
                if "quota_remaining" in data and data["quota_remaining"] < 50:
                    logger.warning(f"Stack Exchange API quota running low: {data['quota_remaining']} remaining")

                for item in data.get("items", []):
                    # Convert Unix timestamps to UTC datetimes
                    created_at = datetime.fromtimestamp(item["creation_date"], timezone.utc)
                    updated_at = None
                    if "last_edit_date" in item:
                        updated_at = datetime.fromtimestamp(item["last_edit_date"], timezone.utc)

                    # Map the raw JSON to our Canonical ForumDocument
                    doc = ForumDocument(
                        external_id=str(item["question_id"]),
                        forum=ForumType.STACKOVERFLOW,
                        forum_name="Stack Overflow",
                        community=self.site,
                        content_type=ContentType.QUESTION,
                        title=html.unescape(item.get("title", "")), # SE returns HTML entities like '
                        body=item.get("body", "Body content not retrieved."),
                        author=item.get("owner", {}).get("display_name", "Unknown"),
                        url=item.get("link", ""),
                        created_at=created_at,
                        updated_at=updated_at,
                        score=item.get("score", 0),
                        answer_count=item.get("answer_count", 0),
                        accepted=item.get("is_answered", False),
                        tags=item.get("tags", []),
                        metadata={
                            "view_count": item.get("view_count", 0),
                            "content_license": item.get("content_license", "")
                        }
                    )
                    documents.append(doc)

            except httpx.HTTPError as e:
                logger.error(f"HTTP Exception for {url} - {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error parsing Stack Exchange data - {str(e)}")

        return documents

    async def get_document(self, external_id: str) -> Optional[ForumDocument]:
        """Fetch a single document by ID (Stubbed for now)"""
        pass

    async def health_check(self) -> bool:
        """Verify the API is reachable"""
        url = f"{self.base_url}/info"
        params = {"site": self.site}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=5.0)
                return response.status_code == 200
            except:
                return False