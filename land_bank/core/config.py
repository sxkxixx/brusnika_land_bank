import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Application config

    # Database config
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    POSTGRES_HOST: str = os.getenv('POSTGRES_HOST')
    POSTGRES_PORT: int = int(os.getenv('POSTGRES_PORT'))
    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')

    # Auth
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ACCESS_TOKEN_TTL_MINUTES: int = int(os.getenv('ACCESS_TOKEN_TTL_MINUTES'))
    REFRESH_TOKEN_TTL_DAYS: int = int(os.getenv('REFRESH_TOKEN_TTL_DAYS'))
    ALGORITHM: str = os.getenv('ALGORITHM')

    # Redis
    REDIS_HOST: str = os.getenv('REDIS_HOST')
    REDIS_PORT: int = int(os.getenv('REDIS_PORT'))

    AWS_ACCESS_KEY_ID: str = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY: str = os.getenv('AWS_SECRET_ACCESS_KEY')
    REGION_NAME: str = os.getenv('REGION_NAME')
    BUCKET_NAME: str = os.getenv('BUCKET_NAME')
    S3_ENDPOINT_URL: str = os.getenv('S3_ENDPOINT_URL')
