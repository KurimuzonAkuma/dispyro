from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from .storages import StateStorage, StorageKey

if TYPE_CHECKING:
    from .state import State


@dataclass
class FSMContext:
    """Injected into handlers as `state: FSMContext`.
    Provides get/set/clear interface over the configured StateStorage.

    Example::

        async def handler(client, message, state: FSMContext):
            await state.set(Form.waiting_name)
            current = await state.get()
            await state.clear()
    """

    storage: StateStorage
    key: StorageKey

    async def get(self) -> str | None:
        """Return the current state string, or None if no state is set."""
        return await self.storage.get(self.key)

    async def set(self, state: State | str | None) -> None:
        """Set the current state. Pass None to clear."""
        if state is None:
            await self.storage.clear(self.key)
        else:
            await self.storage.set(self.key, str(state))

    async def clear(self) -> None:
        """Clear the current state (alias for set(None))."""
        await self.storage.clear(self.key)

    async def get_data(self) -> dict[str, Any]:
        """Return the current context data."""
        return await self.storage.get_data(self.key)

    async def set_data(self, data: dict[str, Any]) -> None:
        """Set the current context data."""
        await self.storage.set_data(self.key, data)

    async def update_data(self, data: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        """Update the current context data with new values."""
        current_data = await self.get_data()
        if data is not None:
            current_data.update(data)
        current_data.update(kwargs)
        await self.set_data(current_data)
        return current_data
