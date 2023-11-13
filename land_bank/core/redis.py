import aioredis
from .config import Config


def get_redis(db: int = 0) -> aioredis.Redis:
    return aioredis.from_url(
        f'redis://{Config.REDIS_PORT}:{Config.REDIS_PORT}/{db}'
    )
