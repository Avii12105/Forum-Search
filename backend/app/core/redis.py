import logging
from redis.asyncio import Redis, from_url
from app.core.config import settings

logger = logging.getLogger(__name__)

redis_client: Redis = None

async def init_redis():
    """Initialize the global async Redis client."""
    global redis_client
    try:
        redis_client = from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)
        await redis_client.ping()
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.warning(f"Could not connect to Redis: {str(e)}. Caching will be disabled.")
        redis_client = None

async def close_redis():
    """Close Redis connection pool on app shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed.")