import logging
from typing import List

from app.schemas.document import ForumDocument

logger = logging.getLogger(__name__)

class Deduplicator:
    @staticmethod
    def deduplicate(documents: List[ForumDocument]) -> List[ForumDocument]:
        if not documents:
            return []

        seen_urls = set()
        unique_documents = []

        # Sort documents by score descending before deduplicating.
        sorted_docs = sorted(documents, key=lambda d: d.score, reverse=True)

        for doc in sorted_docs:
            # 1. Normalize the main URL
            main_url = doc.url.lower().rstrip('/')
            
            # 2. Check for aggregator metadata
            story_url = doc.metadata.get("story_url", "").lower().rstrip('/')

            # Define the set of URLs this document represents
            urls_to_check = {main_url}
            if story_url:
                urls_to_check.add(story_url)

            # If none of this document's URLs have been seen yet, keep it!
            if not seen_urls.intersection(urls_to_check):
                unique_documents.append(doc)
                seen_urls.update(urls_to_check)
            else:
                logger.info(f"Deduplicator filtered out duplicate resource: {main_url}")

        logger.info(f"Deduplication complete: {len(documents)} docs in -> {len(unique_documents)} docs out")
        return unique_documents