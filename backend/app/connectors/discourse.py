import html
import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx

from app.connectors.base import BaseConnector
from app.schemas.document import ForumDocument, ForumType, ContentType

logger = logging.getLogger(__name__)

class DiscourseConnector(BaseConnector):
    """
    Connector for Discourse-powered forums.
    By default, it targets meta.discourse.org, but can be instantiated
    with any public Discourse domain (e.g., https://discuss.python.org).
    """
    
    def __init__(self, domain: str = "https://meta.discourse.org", forum_name: str = "Discourse Meta"):
        # Strip trailing slashes to ensure clean URL construction later
        self.base_url = domain.rstrip('/')
        self.forum_name = forum_name
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "python:forumsearch-engine:v1.0"
        }

    async def search(self, query: str, limit: int = 10) -> List[ForumDocument]:
        """
        Search the Discourse forum for posts matching the query.
        """
        url = f"{self.base_url}/search.json"
        params = {
            "q": query,
            "page": 1
        }

        documents = []
        
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Discourse search returns a 'posts' array and a 'topics' array. 
                # The 'posts' array contains the actual matching content and metadata.
                posts = data.get("posts", [])

                # Discourse doesn't support strict limiting on the API call easily, 
                # so we slice the array to respect our limit parameter.
                for item in posts[:limit]:
                    created_at_str = item.get("created_at")
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.now(timezone.utc)

                    topic_slug = item.get("topic_slug", "topic")
                    topic_id = item.get("topic_id")
                    post_number = item.get("post_number", 1)
                    
                    # Construct the direct canonical URL to the specific post within the topic
                    post_url = f"{self.base_url}/t/{topic_slug}/{topic_id}/{post_number}"

                    doc = ForumDocument(
                        external_id=str(item.get("id")),
                        forum=ForumType.DISCOURSE,
                        forum_name=self.forum_name,
                        # We use the domain name minus protocol as the "community" identifier
                        community=self.base_url.replace("https://", "").replace("http://", ""),
                        content_type=ContentType.DISCUSSION if post_number == 1 else ContentType.COMMENT,
                        title=html.unescape(item.get("topic_title", "Untitled Topic")),
                        # Discourse returns a shortened snippet called 'blurb' for search results
                        body=html.unescape(item.get("blurb", "")).replace("...", ""),
                        author=item.get("username", "Unknown"),
                        url=post_url,
                        created_at=created_at,
                        updated_at=None,
                        score=item.get("like_count", 0),
                        comment_count=0, # Not easily available in the basic search post schema
                        answer_count=0,
                        accepted=False,
                        tags=[],
                        metadata={
                            "post_number": post_number
                        }
                    )
                    documents.append(doc)

            except httpx.HTTPError as e:
                logger.error(f"Discourse HTTP Exception for {url} - {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error parsing Discourse data - {str(e)}")

        return documents

    async def get_document(self, external_id: str) -> Optional[ForumDocument]:
        """Fetch a single item by ID (Stubbed for now)"""
        pass

    async def health_check(self) -> bool:
        """Verify the Discourse API is reachable"""
        url = f"{self.base_url}/site.json"
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url, timeout=5.0)
                return response.status_code == 200
            except:
                return False