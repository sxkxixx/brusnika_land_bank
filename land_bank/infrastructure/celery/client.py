import celery

from infrastructure.settings import RedisSettings

_URL = f'redis://{RedisSettings.REDIS_HOST}:{RedisSettings.REDIS_PORT}'

celery_client = celery.Celery(
    'tasks',
    broker=_URL,
    backend=_URL
)
