import os

from dotenv import load_dotenv

load_dotenv()

__all__ = [
    'DatabaseSettings',
    'AppSettings',
    'SMTPSettings',
    'AMQPSettings',
    'S3Settings',
    'RedisSettings',
    'TestDatabaseSettings'
]


class DatabaseSettings:
    # Database config
    POSTGRES_DB: str = os.getenv('POSTGRES_DB', 'postgres')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT: int = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_USER: str = os.getenv('POSTGRES_USER', 'root')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD', '')


class AppSettings:
    # Auth
    SECRET_KEY: str = os.getenv('SECRET_KEY', '')
    ACCESS_TOKEN_TTL_MINUTES: int = int(
        os.getenv('ACCESS_TOKEN_TTL_MINUTES', ''))
    REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv('REFRESH_TOKEN_TTL_DAYS', ''))
    ALGORITHM: str = os.getenv('ALGORITHM', '')

    # CORS
    FRONTEND_HOST: str = os.getenv('FRONTEND_HOST', '')
    TESTING_APP: bool = bool(os.getenv('TESTING_APP', False))


class RedisSettings:
    # Redis
    REDIS_HOST: str = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT', 6379))


class S3Settings:
    # AWS S3
    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    REGION_NAME: str = os.getenv('REGION_NAME', '')
    BUCKET_NAME: str = os.getenv('BUCKET_NAME', '')
    S3_ENDPOINT_URL: str = os.getenv('S3_ENDPOINT_URL', '')


class SMTPSettings:
    # SMTP Protocol settings
    EMAIL: str = os.getenv('SMTP_EMAIL', '')
    PASSWORD: str = os.getenv('SMTP_PASSWORD', '')
    HOST: str = os.getenv('SMTP_SERVER', '')
    PORT: int = int(os.getenv('SMTP_PORT', 0))


class AMQPSettings:
    AMQP_HOST: str = os.getenv('AMQP_HOST', '')
    AMQP_PORT: str = os.getenv('AMQP_PORT', '')


class TestDatabaseSettings:
    TEST_DB: str = os.getenv('TEST_DB', 'postgres')
    TEST_HOST: str = os.getenv('TEST_HOST', 'localhost')
    TEST_PORT: int = int(os.getenv('TEST_PORT', 5432))
    TEST_USER: str = os.getenv('TEST_USER', 'root')
    TEST_PASSWORD: str = os.getenv('TEST_PASSWORD', '')

    @classmethod
    def url(cls) -> str:
        return (
            f'postgresql+asyncpg://'
            f'{cls.TEST_USER}'
            f':{cls.TEST_PASSWORD}'
            f'@{cls.TEST_HOST}'
            f':{cls.TEST_PORT}'
            f'/{cls.TEST_DB}'
        )
