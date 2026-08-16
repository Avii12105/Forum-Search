import json
import logging
from typing import List, Optional
from app.schemas.document import ForumDocument
from app.core.config import settings
import app.core.redis as redis_module

logger = logging.getLogger(__name__)

class CacheService:
    @staticmethod
    def _generate_cache_key(query: str, limit: int, forums: Optional[List[str]], min_score: int, accepted_only: bool) -> str:
        normalized_q = query.strip().lower()
        forums_str = ",".join(sorted(forums)) if forums else "all"
        return f"search:{normalized_q}:limit:{limit}:forums:{forums_str}:score:{min_score}:acc:{accepted_only}"

    async def get_cached_search(self, query: str, limit: int, forums: Optional[List[str]] = None, min_score: int = 0, accepted_only: bool = False) -> Optional[List[ForumDocument]]:
        client = redis_module.redis_client
        if not client: return None

        key = self._generate_cache_key(query, limit, forums, min_score, accepted_only)
        try:
            cached_data = await client.get(key)
            if cached_data:
                logger.info(f"CACHE HIT for key: {key}")
                raw_list = json.loads(cached_data)
                return [ForumDocument.model_validate(doc) for doc in raw_list]
        except Exception as e:
            logger.error(f"Cache read error: {e}")
        return None

    async def set_cached_search(self, query: str, limit: int, documents: List[ForumDocument], forums: Optional[List[str]] = None, min_score: int = 0, accepted_only: bool = False):
        client = redis_module.redis_client
        if not client or not documents: return

        key = self._generate_cache_key(query, limit, forums, min_score, accepted_only)
        try:
            serializable_list = [doc.model_dump(mode="json") for doc in documents]
            await client.setex(name=key, time=settings.CACHE_TTL_SECONDS, value=json.dumps(serializable_list))
            logger.info(f"CACHE SET for key: {key}")
        except Exception as e:
            logger.error(f"Cache write error: {e}")