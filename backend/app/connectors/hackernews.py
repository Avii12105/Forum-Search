import html
import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx

from app.connectors.base import BaseConnector
from app.schemas.document import ForumDocument, ForumType, ContentType

logger = logging.getLogger(__name__)

class HackerNewsConnector(BaseConnector):
    """
    Connector for Hacker News via the official Algolia-powered Search API.
    API Docs: https://hn.algolia.com/api
    """
    
    def __init__(self):
        self.base_url = "https://hn.algolia.com/api/v1"

    async def search(self, query: str, limit: int = 10) -> List[ForumDocument]:
        """
        Search Hacker News stories matching the query.
        """
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "tags": "story", # Restrict to top-level stories/discussions only
            "hitsPerPage": limit
        }

        documents = []
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                hits = data.get("hits", [])

                for item in hits:
                    # HN Algolia provides an ISO 8601 string in created_at
                    created_at_str = item.get("created_at")
                    if created_at_str:
                        # Replace 'Z' with '+00:00' for safe Python parsing
                        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    else:
                        created_at = datetime.now(timezone.utc)

                    object_id = item.get("objectID")
                    title = item.get("title") or item.get("story_title", "Untitled HN Discussion")
                    
                    # If it's an "Ask HN" it might not have an external URL, link to the discussion instead
                    url_link = item.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
                    
                    doc = ForumDocument(
                        external_id=str(object_id),
                        forum=ForumType.HACKERNEWS,
                        forum_name="Hacker News",
                        community="HN",
                        content_type=ContentType.DISCUSSION,
                        title=html.unescape(title),
                        body=html.unescape(item.get("story_text", "") or "External link discussion."),
                        author=item.get("author", "Unknown"),
                        url=url_link,
                        created_at=created_at,
                        updated_at=None,
                        score=item.get("points", 0),
                        comment_count=item.get("num_comments", 0),
                        answer_count=0,
                        accepted=False,
                        tags=["tech", "programming"],
                        metadata={
                            "story_url": item.get("url", "")
                        }
                    )
                    documents.append(doc)

            except httpx.HTTPError as e:
                logger.error(f"Hacker News HTTP Exception: {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error parsing Hacker News data: {str(e)}")

        return documents

    async def get_document(self, external_id: str) -> Optional[ForumDocument]:
        """Fetch a single item by ID (Stubbed for now)"""
        pass

    async def health_check(self) -> bool:
        """Verify Algolia HN search API is reachable"""
        url = f"{self.base_url}/search?query=test&tags=story&hitsPerPage=1"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=5.0)
                return response.status_code == 200
            except:
                return False