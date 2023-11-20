import aioredis
from .config import Config

redis = aioredis.Redis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
)

# def get_redis(db: int = 0) -> aioredis.Redis:
#     return aioredis.from_url(
#         f'redis://{Config.REDIS_PORT}:{Config.REDIS_PORT}/{db}'
#     )
