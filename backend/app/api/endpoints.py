from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.document import ForumDocument
from app.services.search import SearchEngine
from app.services.cache import CacheService
from app.core.database import get_db
from app.repositories.document import DocumentRepository

router = APIRouter()
search_engine = SearchEngine()
cache_service = CacheService()

@router.get("/search", response_model=List[ForumDocument], summary="Execute cross-forum search")
async def perform_search(
    q: str = Query(..., description="The search query"),
    limit: int = Query(10, description="Results to fetch per forum", ge=1, le=50),
    forums: Optional[List[str]] = Query(None, description="List of forums to include (e.g. github, stackexchange)"),
    min_score: int = Query(5, description="Minimum upvotes required"),
    accepted_only: bool = Query(False, description="Only return accepted/resolved threads"),
    db: AsyncSession = Depends(get_db)
):
    # 1. Check Cache
    cached_results = await cache_service.get_cached_search(q, limit, forums, min_score, accepted_only)
    if cached_results is not None:
        return cached_results

    # 2. Execute Search with filters
    results = await search_engine.execute_search(
        query=q, 
        limit_per_source=limit, 
        db=db,
        forums=forums,
        min_score=min_score,
        accepted_only=accepted_only
    )

    # 3. Store in Cache
    await cache_service.set_cached_search(q, limit, results, forums, min_score, accepted_only)

    return results

@router.get("/autocomplete", response_model=List[str], summary="Get search suggestions")
async def autocomplete_search(
    q: str = Query(..., min_length=2, description="The partial search query"),
    db: AsyncSession = Depends(get_db)
):
    """
    Returns a list of suggested forum titles from our locally indexed Postgres database.
    """
    repo = DocumentRepository(db)
    suggestions = await repo.get_autocomplete_suggestions(query=q)
    return suggestions