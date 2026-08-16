import html
import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx

from app.connectors.base import BaseConnector
from app.schemas.document import ForumDocument, ForumType, ContentType

logger = logging.getLogger(__name__)

class LemmyConnector(BaseConnector):
    """
    Connector for Lemmy (Federated Reddit alternative) using API v3.
    Defaults to lemmy.ml, but can be instantiated with any instance.
    API Docs: https://join-lemmy.org/api/classes/LemmyHttp.html
    """
    
    def __init__(self, instance_url: str = "https://lemmy.ml"):
        self.base_url = instance_url.rstrip('/')
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "python:forumsearch-engine:v1.0"
        }

    async def search(self, query: str, limit: int = 10) -> List[ForumDocument]:
        """
        Search the Lemmy instance for posts.
        """
        url = f"{self.base_url}/api/v3/search"
        params = {
            "q": query,
            "type_": "Posts",  # Only search for Posts (not Comments/Users)
            "limit": limit,
            "sort": "TopAll"   # Relevance sorting varies by instance, TopAll is reliable
        }

        documents = []
        
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                # Lemmy nests its data cleanly into post, community, creator, and counts
                posts = data.get("posts", [])

                for item in posts:
                    post = item.get("post", {})
                    community = item.get("community", {})
                    creator = item.get("creator", {})
                    counts = item.get("counts", {})

                    # Handle timestamp - Lemmy usually returns 'YYYY-MM-DDTHH:MM:SS.mmmmmm'
                    published_str = post.get("published")
                    if published_str:
                        # Append Z if missing so fromisoformat parses it as UTC
                        if not published_str.endswith("Z"):
                            published_str += "Z"
                        created_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                    else:
                        created_at = datetime.now(timezone.utc)

                    # Determine URL: ActivityPub ID is the canonical remote link, 
                    # otherwise fallback to local instance link
                    post_url = post.get("ap_id") or f"{self.base_url}/post/{post.get('id')}"
                    
                    # Formatting community name (e.g. 'c/technology' or 'c/technology@otherinstance.com')
                    actor_id = community.get("actor_id", "")
                    community_domain = actor_id.split("/")[-2] if actor_id else "unknown"
                    community_name = f"c/{community.get('name', 'unknown')}@{community_domain}"

                    doc = ForumDocument(
                        external_id=str(post.get("id")),
                        forum=ForumType.LEMMY,
                        forum_name="Lemmy",
                        community=community_name,
                        content_type=ContentType.DISCUSSION,
                        title=html.unescape(post.get("name", "Untitled")),
                        body=html.unescape(post.get("body", "")),
                        author=creator.get("name", "Unknown"),
                        url=post_url,
                        created_at=created_at,
                        updated_at=None,
                        score=counts.get("score", 0),
                        comment_count=counts.get("comments", 0),
                        answer_count=0,
                        accepted=False,
                        tags=[],
                        metadata={
                            "upvotes": counts.get("upvotes", 0),
                            "downvotes": counts.get("downvotes", 0),
                            "is_nsfw": post.get("nsfw", False)
                        }
                    )
                    documents.append(doc)

            except httpx.HTTPError as e:
                logger.error(f"Lemmy HTTP Exception for {url} - {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error parsing Lemmy data - {str(e)}")

        return documents

    async def get_document(self, external_id: str) -> Optional[ForumDocument]:
        """Fetch a single item by ID"""
        pass

    async def health_check(self) -> bool:
        """Verify the Lemmy API is reachable"""
        url = f"{self.base_url}/api/v3/site"
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url, timeout=5.0)
                return response.status_code == 200
            except:
                return False