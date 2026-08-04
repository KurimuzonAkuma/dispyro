from abc import ABC, abstractmethod
from typing import NamedTuple


class StorageKey(NamedTuple):
    chat_id: int
    user_id: int


class StateStorage(ABC):
    @abstractmethod
    async def get(self, key: StorageKey) -> str | None: ...

    @abstractmethod
    async def set(self, key: StorageKey, state: str) -> None: ...

    @abstractmethod
    async def clear(self, key: StorageKey) -> None: ...


class MemoryStorage(StateStorage):
    def __init__(self) -> None:
        self._data: dict[StorageKey, str] = {}

    async def get(self, key: StorageKey) -> str | None:
        return self._data.get(key)

    async def set(self, key: StorageKey, state: str) -> None:
        self._data[key] = state

    async def clear(self, key: StorageKey) -> None:
        self._data.pop(key, None)


class RedisStorage(StateStorage):
    def __init__(self, redis, ttl: int | None = None) -> None:  # noqa: ANN001
        try:
            import redis as _  # noqa: F401, PLC0415
        except ImportError:
            raise ImportError(
                "redis package is required for RedisStorage. Install it with: pip install dispyro[redis]",
            ) from None

        self._redis = redis
        self._ttl = ttl

    def _make_key(self, key: StorageKey) -> str:
        return f"fsm:{key.chat_id}:{key.user_id}"

    async def get(self, key: StorageKey) -> str | None:
        value = await self._redis.get(self._make_key(key))
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

    async def set(self, key: StorageKey, state: str) -> None:
        redis_key = self._make_key(key)
        await self._redis.set(redis_key, state)
        if self._ttl is not None:
            await self._redis.expire(redis_key, self._ttl)

    async def clear(self, key: StorageKey) -> None:
        await self._redis.delete(self._make_key(key))
