from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

from .storages import StateStorage, StorageKey

if TYPE_CHECKING:
    from .states import State


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

    async def set(self, state: Union["State", str, None]) -> None:
        """Set the current state. Pass None to clear."""
        if state is None:
            await self.storage.clear(self.key)
        else:
            await self.storage.set(self.key, str(state))

    async def clear(self) -> None:
        """Clear the current state (alias for set(None))."""
        await self.storage.clear(self.key)
