from abc import ABC, abstractmethod
from typing import Any, NamedTuple


class StorageKey(NamedTuple):
    chat_id: int
    user_id: int
    thread_id: int | None = None


class StateStorage(ABC):
    @abstractmethod
    async def get(self, key: StorageKey) -> str | None: ...

    @abstractmethod
    async def set(self, key: StorageKey, state: str) -> None: ...

    @abstractmethod
    async def clear(self, key: StorageKey) -> None: ...

    @abstractmethod
    async def get_data(self, key: StorageKey) -> dict[str, Any]: ...

    @abstractmethod
    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None: ...


class MemoryStorage(StateStorage):
    def __init__(self) -> None:
        self._data: dict[StorageKey, str] = {}
        self._fsm_data: dict[StorageKey, dict[str, Any]] = {}

    async def get(self, key: StorageKey) -> str | None:
        return self._data.get(key)

    async def set(self, key: StorageKey, state: str) -> None:
        self._data[key] = state

    async def clear(self, key: StorageKey) -> None:
        self._data.pop(key, None)
        self._fsm_data.pop(key, None)

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return self._fsm_data.get(key, {}).copy()

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        self._fsm_data[key] = data.copy()


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
        base = f"fsm:{key.chat_id}:{key.user_id}"
        if key.thread_id is not None:
            return f"{base}:{key.thread_id}"
        return base

    def _make_data_key(self, key: StorageKey) -> str:
        return f"{self._make_key(key)}:data"

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

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        import json
        value = await self._redis.get(self._make_data_key(key))
        if value is None:
            return {}
        return json.loads(value.decode() if isinstance(value, bytes) else value)

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        import json
        redis_key = self._make_data_key(key)
        await self._redis.set(redis_key, json.dumps(data))
        if self._ttl is not None:
            await self._redis.expire(redis_key, self._ttl)

    async def clear(self, key: StorageKey) -> None:
        await self._redis.delete(self._make_key(key), self._make_data_key(key))
