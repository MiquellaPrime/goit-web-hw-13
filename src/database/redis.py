import redis

from src.settings import settings


def get_redis():
    return redis.Redis(host=settings.redis.host, port=settings.redis.port, db=0)
