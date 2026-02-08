from redis import asyncio as aioredis

from common_lib.config.settings import settings

redis_client = None


async def init_redis():
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL)
    return redis_client


async def get_redis():
    global redis_client
    if redis_client is None:
        redis_client = await init_redis()
    return redis_client
