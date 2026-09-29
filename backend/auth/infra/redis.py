import redis.asyncio as redis
from config import RedisConfig


def new_redis_client(config: RedisConfig) -> redis.Redis:
    return redis.Redis(
        host=config.host,
        port=config.port,
        password=config.password,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        health_check_interval=30,
        max_connections=15,
    )
