import json
import logging
from typing import Optional, Any
from datetime import datetime, timezone
import redis

from app.config import get_settings

logger = logging.getLogger("maskit.redis")
settings = get_settings()

class RedisService:
    """
    Redis client wrapper with automatic graceful fallback to in-memory state
    if Redis is offline or unreachable.
    """
    def __init__(self):
        self._memory_cache = {}
        self._rate_limits = {}
        self.is_connected = False
        self.client = None
        self._connect()

    def _connect(self):
        try:
            self.client = redis.from_url(settings.REDIS_URL, decode_responses=True, socket_timeout=1.5)
            self.client.ping()
            self.is_connected = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self.is_connected = False
            self.client = None
            logger.warning(f"Redis unavailable ({e}). Using in-memory fallback mode.")

    def ping(self) -> bool:
        if not self.is_connected or self.client is None:
            return False
        try:
            return bool(self.client.ping())
        except Exception:
            self.is_connected = False
            return False

    def get(self, key: str) -> Optional[str]:
        if self.is_connected and self.client:
            try:
                return self.client.get(key)
            except Exception:
                self.is_connected = False
        return self._memory_cache.get(key)

    def set(self, key: str, value: str, ex_seconds: Optional[int] = None) -> bool:
        if self.is_connected and self.client:
            try:
                self.client.set(key, value, ex=ex_seconds)
                return True
            except Exception:
                self.is_connected = False
        self._memory_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        if self.is_connected and self.client:
            try:
                self.client.delete(key)
                return True
            except Exception:
                self.is_connected = False
        self._memory_cache.pop(key, None)
        return True

    def check_rate_limit(self, identifier: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Returns True if within rate limit, False if rate limit exceeded."""
        key = f"rl:{identifier}"
        if self.is_connected and self.client:
            try:
                current = self.client.incr(key)
                if current == 1:
                    self.client.expire(key, window_seconds)
                return current <= max_requests
            except Exception:
                self.is_connected = False

        # In-memory fallback
        now = datetime.now(timezone.utc).timestamp()
        record = self._rate_limits.get(key, {"count": 0, "reset": now + window_seconds})
        if now > record["reset"]:
            record = {"count": 1, "reset": now + window_seconds}
        else:
            record["count"] += 1
        self._rate_limits[key] = record
        return record["count"] <= max_requests

_redis_instance = None

def get_redis_service() -> RedisService:
    global _redis_instance
    if _redis_instance is None:
        _redis_instance = RedisService()
    return _redis_instance
