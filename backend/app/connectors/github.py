import logging
from datetime import datetime, timezone
from typing import List, Optional
import httpx

from app.connectors.base import BaseConnector
from app.schemas.document import ForumDocument, ForumType, ContentType

logger = logging.getLogger(__name__)

class GitHubConnector(BaseConnector):
    """
    Connector for GitHub's public Search API (targeting Issues & Pull Requests).
    API Docs: https://docs.github.com/rest/search/search#search-issues-and-pull-requests
    """
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "python:forumsearch-engine:v1.0"
            # Unauthenticated search is limited to 10 req/min. 
            # To increase this later, add: "Authorization": "Bearer YOUR_GITHUB_TOKEN"
        }

    async def search(self, query: str, limit: int = 10) -> List[ForumDocument]:
        """
        Search GitHub for issues or PRs matching the query.
        """
        url = f"{self.base_url}/search/issues"
        params = {
            "q": f"{query} is:public", # Ensure we only search public repos
            "per_page": limit,
            "sort": "relevance"
        }

        documents = []
        
        async with httpx.AsyncClient(headers=self.headers, follow_redirects=True) as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                
                # Gracefully handle GitHub's strict 10 req/min rate limit for unauthenticated users
                if response.status_code == 403:
                    logger.warning("GitHub API rate limit exceeded. Skipping GitHub.")
                    return []
                    
                response.raise_for_status()
                data = response.json()
                
                items = data.get("items", [])

                for item in items:
                    # Parse ISO timestamps safely
                    created_at_str = item.get("created_at")
                    created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")) if created_at_str else datetime.now(timezone.utc)
                    
                    updated_at_str = item.get("updated_at")
                    updated_at = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00")) if updated_at_str else None

                    # Extract repository name (e.g., 'facebook/react') from the repo URL
                    repo_url = item.get("repository_url", "")
                    community_name = repo_url.replace("https://api.github.com/repos/", "") if repo_url else "github"

                    # Map labels to tags
                    tags = [label.get("name") for label in item.get("labels", []) if isinstance(label, dict)]

                    # Use reactions total count for score if available, otherwise 0
                    reactions = item.get("reactions", {})
                    score = reactions.get("total_count", 0)

                    doc = ForumDocument(
                        external_id=str(item.get("id")),
                        forum=ForumType.GITHUB,
                        forum_name="GitHub",
                        community=community_name,
                        content_type=ContentType.DISCUSSION, 
                        title=item.get("title", "Untitled Issue"),
                        body=item.get("body", "") or "No description provided.",
                        author=item.get("user", {}).get("login", "Unknown"),
                        url=item.get("html_url", ""),
                        created_at=created_at,
                        updated_at=updated_at,
                        score=score,
                        comment_count=item.get("comments", 0),
                        answer_count=0,
                        # A closed issue/PR is loosely considered "resolved" in this context
                        accepted=item.get("state") == "closed", 
                        tags=tags,
                        metadata={
                            "state": item.get("state", "open"),
                            "is_pull_request": "pull_request" in item
                        }
                    )
                    documents.append(doc)

            except httpx.HTTPError as e:
                logger.error(f"GitHub HTTP Exception for {url} - {str(e)}")
            except Exception as e:
                logger.error(f"Unexpected error parsing GitHub data - {str(e)}")

        return documents

    async def get_document(self, external_id: str) -> Optional[ForumDocument]:
        pass

    async def health_check(self) -> bool:
        """Verify GitHub API is reachable via its zen endpoint"""
        url = f"{self.base_url}/zen" 
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.get(url, timeout=5.0)
                return response.status_code == 200 or response.status_code == 403
            except:
                return False