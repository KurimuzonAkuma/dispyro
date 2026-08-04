from __future__ import annotations

# This file defines custom handlers definitions that is used instead of
# original Pyrogram handlers. Unlike original handlers, customs are DI-friendly,
# providing ability to use dependency injection with ease.
#
# Groups were removed because of changed processing logic (actual handlers
# distribution instead of formal split by groups, which made groups useless).
# Instead of them, new attribute added: `priority`, which affects on handlers
# order inside of specific router. Lower number means higher priority (highest
# priority is 1), handlers with same priority arranged corresponding to order
# in which they were registered. By default, all registered handlers priority
# is set to 1. You can customize this behaviour by providing your own
# `priority_factory`. This function must take 2 arguments
# (handler itself and `router` that registering this handler) and return
# positive `int`.
from typing import Generic, TypeVar

import dispyro

from .filters import Filter
from .types import AnyFilter, Callback
from .types.contexts import UpdateContext
from .types.signatures import (
    CallbackQueryHandlerCallback,
    ChatMemberUpdatedHandlerCallback,
    ChosenInlineResultHandlerCallback,
    DeletedMessagesHandlerCallback,
    EditedMessageHandlerCallback,
    InlineQueryHandlerCallback,
    MessageHandlerCallback,
    PollHandlerCallback,
    PriorityFactory,
    RawUpdateHandlerCallback,
    UserStatusHandlerCallback,
)
from .utils import safe_call

CallbackT = TypeVar("CallbackT", bound=Callback)


def default_priority_factory(_: Handler, __: dispyro.Router) -> int:
    return 1


class Handler(Generic[CallbackT]):
    _priority_factory: PriorityFactory | None = None

    @classmethod
    def set_priority_factory(cls, priority_factory: PriorityFactory) -> None:
        cls._priority_factory = priority_factory

    def __init__(
        self,
        *,
        callback: CallbackT,
        router: dispyro.Router,
        name: str | None = None,
        priority: int | None = None,
        filters: AnyFilter = Filter(),
    ) -> None:
        if priority is not None:
            self._priority = priority
        else:
            factory = self._priority_factory or default_priority_factory
            self._priority = factory(self, router)

        self._name = name or "unnamed_handler"
        self.callback: CallbackT = safe_call(callable=callback)  # pyright: ignore [reportAttributeAccessIssue]
        self._router = router
        self._filters: Filter = Filter() & filters

    async def __call__(self, context: UpdateContext) -> bool:
        filters_passed = await self._filters(context=context)

        if not filters_passed:
            return False

        await self.callback(context.client, context.update, **context.data)  # pyright: ignore [reportArgumentType]
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} `{self._name}`"


class CallbackQueryHandler(Handler[CallbackQueryHandlerCallback]):
    pass


class ChatMemberUpdatedHandler(Handler[ChatMemberUpdatedHandlerCallback]):
    pass


class ChosenInlineResultHandler(Handler[ChosenInlineResultHandlerCallback]):
    pass


class DeletedMessagesHandler(Handler[DeletedMessagesHandlerCallback]):
    pass


class EditedMessageHandler(Handler[EditedMessageHandlerCallback]):
    pass


class InlineQueryHandler(Handler[InlineQueryHandlerCallback]):
    pass


class MessageHandler(Handler[MessageHandlerCallback]):
    pass


class PollHandler(Handler[PollHandlerCallback]):
    pass


class RawUpdateHandler(Handler[RawUpdateHandlerCallback]):
    pass


class UserStatusHandler(Handler[UserStatusHandlerCallback]):
    pass
