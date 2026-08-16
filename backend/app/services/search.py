import asyncio
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.document import ForumDocument
from app.connectors.stackexchange import StackExchangeConnector
from app.connectors.hackernews import HackerNewsConnector
from app.connectors.discourse import DiscourseConnector
from app.connectors.lemmy import LemmyConnector
from app.connectors.github import GitHubConnector
from app.repositories.document import DocumentRepository
from app.services.ranking.composite import CompositeRanker
from app.services.deduplicator import Deduplicator
from app.services.vector import VectorService

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        self.connectors = [
            StackExchangeConnector(),
            HackerNewsConnector(),
            DiscourseConnector(), 
            LemmyConnector(),
            GitHubConnector(),
        ]
        self.ranking_engine = CompositeRanker()
        self.deduplicator = Deduplicator()
        self.vector_service = VectorService()

    async def execute_search(
        self, 
        query: str, 
        limit_per_source: int = 10,
        db: Optional[AsyncSession] = None,
        forums: Optional[List[str]] = None,    # <--- New parameter
        min_score: int = 0,                    # <--- New parameter
        accepted_only: bool = False            # <--- New parameter
    ) -> List[ForumDocument]:
        
        if not query.strip(): return []

        # 1. Pre-fetch filtering: Only use requested connectors
        active_connectors = self.connectors
        if forums:
            active_connectors = [
                c for c in self.connectors 
                # e.g., matches "github" to "GitHubConnector"
                if c.__class__.__name__.lower().replace("connector", "") in [f.lower() for f in forums]
            ]

        tasks = [c.search(query=query, limit=limit_per_source) for c in active_connectors]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated_documents: List[ForumDocument] = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Connector failed: {result}")
            elif isinstance(result, list):
                aggregated_documents.extend(result)

        if aggregated_documents:
            # 2. Post-fetch filtering: Apply minimums and status
            filtered_docs = []
            for doc in aggregated_documents:
                if doc.score < min_score:
                    continue
                if accepted_only and not doc.accepted:
                    continue
                filtered_docs.append(doc)
            
            aggregated_documents = filtered_docs

            # Continue standard pipeline if documents survived the filters
            if aggregated_documents:
                aggregated_documents = self.deduplicator.deduplicate(aggregated_documents)
                self.vector_service.upsert_documents(aggregated_documents)
                semantic_scores = self.vector_service.semantic_search(query, n_results=len(aggregated_documents))
                scores = self.ranking_engine.rank(query, aggregated_documents, semantic_scores)
                
                aggregated_documents.sort(key=lambda doc: scores.get(doc.external_id, 0.0), reverse=True)

                if db:
                    repo = DocumentRepository(db)
                    await repo.upsert_documents(aggregated_documents)

        return aggregated_documents