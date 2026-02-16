import redis.asyncio as redis
from typing import Optional
from shared.config import settings

class RedisManager:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        if self.client:
            return

        try:
            self.client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=settings.DECODE_RESPONSES
            )
            await self.client.ping()
            print("Connected to Redis.")
        except Exception as e:
            print(f"Redis connection failed: {e}")
            raise e

    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None
            print("Redis connection closed.")

    def get_client(self) -> redis.Redis:
        if not self.client:
            raise RuntimeError("Redis not initialized.")
        return self.client

redis_manager = RedisManager()