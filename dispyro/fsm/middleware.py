from __future__ import annotations

from typing import TYPE_CHECKING

from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    User,
)

from dispyro.middlewares import BaseMiddleware
from dispyro.types import Update
from dispyro.types.contexts import UpdateContext

from .context import FSMContext
from .storages import StateStorage, StorageKey
from .strategy import FSMStrategy

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


def resolve_storage_key(chat_id: int | None, user_id: int, strategy: FSMStrategy) -> StorageKey:
    if chat_id is None:
        chat_id = user_id

    if strategy == FSMStrategy.USER_IN_CHAT:
        return StorageKey(chat_id=chat_id, user_id=user_id)

    if strategy == FSMStrategy.CHAT_ONLY:
        return StorageKey(chat_id=chat_id, user_id=chat_id)

    if strategy == FSMStrategy.GLOBAL_USER:
        return StorageKey(chat_id=user_id, user_id=user_id)

    return StorageKey(chat_id=chat_id, user_id=user_id)


def extract_key(update: Update, strategy: FSMStrategy) -> StorageKey | None:
    """Extract a StorageKey according to the selected FSMStrategy.
    Returns None for update types that have no identifiable sender.
    """

    key = None

    if isinstance(update, Message):
        if update.from_user is None:
            return None

        key = resolve_storage_key(update.chat.id, update.from_user.id, strategy)

    elif isinstance(update, CallbackQuery):
        chat_id = update.message.chat.id if update.message else None
        key = resolve_storage_key(chat_id, update.from_user.id, strategy)

    elif isinstance(update, ChatMemberUpdated):
        key = resolve_storage_key(update.chat.id, update.new_chat_member.user.id, strategy)

    elif isinstance(update, (InlineQuery, ChosenInlineResult)):
        key = resolve_storage_key(None, update.from_user.id, strategy)

    elif isinstance(update, User):
        key = resolve_storage_key(None, update.id, strategy)

    return key


class FSMMiddleware(BaseMiddleware):
    """Middleware that extracts a StorageKey from the current update and injects
    an `FSMContext` into handler dependencies under the name ``state``.

    Register as an outer middleware on the dispatcher or a specific router::

        storage = MemoryStorage()
        dispatcher.message.outer_middleware(FSMMiddleware(storage))
    """

    def __init__(self, storage: StateStorage, strategy: FSMStrategy = FSMStrategy.USER_IN_CHAT) -> None:
        super().__init__()
        self.storage = storage
        self.strategy = strategy

    async def __call__(self, context: UpdateContext) -> AsyncGenerator[None, None]:
        key = extract_key(context.update, self.strategy)

        if key is not None:
            context.data["state"] = FSMContext(storage=self.storage, key=key)

        yield
