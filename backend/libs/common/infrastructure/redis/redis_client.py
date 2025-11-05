import aioredis

redis = None


async def init_redis(url: str):
    global redis
    redis = await aioredis.from_url(url, decode_responses=True)
    return redis
