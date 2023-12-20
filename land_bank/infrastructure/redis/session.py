import aioredis
from infrastructure.settings import RedisSettings

redis = aioredis.Redis(
    host=RedisSettings.REDIS_HOST,
    port=RedisSettings.REDIS_PORT,
)