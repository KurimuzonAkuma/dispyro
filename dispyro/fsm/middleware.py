from typing import Optional

from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    User,
)

from ..middlewares import BaseMiddleware
from ..types.contexts import UpdateContext
from ..types import Update
from .context import FSMContext
from .storages import StateStorage, StorageKey
from .strategy import FSMStrategy


def resolve_storage_key(
    chat_id: Optional[int], user_id: int, strategy: FSMStrategy
) -> StorageKey:
    if chat_id is None:
        chat_id = user_id

    if strategy == FSMStrategy.USER_IN_CHAT:
        return StorageKey(chat_id=chat_id, user_id=user_id)
    elif strategy == FSMStrategy.CHAT_ONLY:
        return StorageKey(chat_id=chat_id, user_id=chat_id)
    elif strategy == FSMStrategy.GLOBAL_USER:
        return StorageKey(chat_id=user_id, user_id=user_id)

    return StorageKey(chat_id=chat_id, user_id=user_id)


def extract_key(update: Update, strategy: FSMStrategy) -> Optional[StorageKey]:
    """Extract a StorageKey according to the selected FSMStrategy.
    Returns None for update types that have no identifiable sender.
    """
    if isinstance(update, Message):
        if update.from_user is None:
            return None
        return resolve_storage_key(update.chat.id, update.from_user.id, strategy)

    if isinstance(update, CallbackQuery):
        chat_id = update.message.chat.id if update.message else None
        return resolve_storage_key(chat_id, update.from_user.id, strategy)

    if isinstance(update, ChatMemberUpdated):
        return resolve_storage_key(update.chat.id, update.new_chat_member.user.id, strategy)

    if isinstance(update, InlineQuery):
        return resolve_storage_key(None, update.from_user.id, strategy)

    if isinstance(update, ChosenInlineResult):
        return resolve_storage_key(None, update.from_user.id, strategy)

    if isinstance(update, User):
        return resolve_storage_key(None, update.id, strategy)

    return None


class FSMMiddleware(BaseMiddleware):
    """Middleware that extracts a StorageKey from the current update and injects
    an `FSMContext` into handler dependencies under the name ``state``.

    Register as an outer middleware on the dispatcher or a specific router::

        storage = MemoryStorage()
        dispatcher.message.outer_middleware(FSMMiddleware(storage))
    """

    def __init__(
        self, 
        storage: StateStorage, 
        strategy: FSMStrategy = FSMStrategy.USER_IN_CHAT
    ) -> None:
        super().__init__()
        self.storage = storage
        self.strategy = strategy

    async def __call__(self, context: UpdateContext):
        key = extract_key(context.update, self.strategy)
        if key is not None:
            context.data["state"] = FSMContext(storage=self.storage, key=key)
        yield
