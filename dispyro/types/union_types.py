from typing import Union

import pyrogram
from pyrogram.types import CallbackQuery, ChatMemberUpdated, ChosenInlineResult, InlineQuery, Message, Poll, User

import dispyro

from . import PackedRawUpdate
from .signatures import (
    CallbackQueryHandlerCallback,
    ChatMemberUpdatedHandlerCallback,
    ChosenInlineResultHandlerCallback,
    DeletedMessagesHandlerCallback,
    EditedMessageHandlerCallback,
    InlineQueryHandlerCallback,
    MessageHandlerCallback,
    PollHandlerCallback,
    RawUpdateHandlerCallback,
    UserStatusHandlerCallback,
)

Handler = Union[
    "dispyro.handlers.CallbackQueryHandler",
    "dispyro.handlers.ChatMemberUpdatedHandler",
    "dispyro.handlers.ChosenInlineResultHandler",
    "dispyro.handlers.DeletedMessagesHandler",
    "dispyro.handlers.EditedMessageHandler",
    "dispyro.handlers.InlineQueryHandler",
    "dispyro.handlers.MessageHandler",
    "dispyro.handlers.PollHandler",
    "dispyro.handlers.UserStatusHandler",
    "dispyro.handlers.RawUpdateHandler",
]

Callback = (
    CallbackQueryHandlerCallback
    | ChatMemberUpdatedHandlerCallback
    | ChosenInlineResultHandlerCallback
    | DeletedMessagesHandlerCallback
    | EditedMessageHandlerCallback
    | InlineQueryHandlerCallback
    | MessageHandlerCallback
    | PollHandlerCallback
    | UserStatusHandlerCallback
    | RawUpdateHandlerCallback
)

Update = (
    CallbackQuery
    | ChatMemberUpdated
    | ChosenInlineResult
    | Message
    | list[Message]
    | InlineQuery
    | Poll
    | User
    | PackedRawUpdate
)

AnyFilter = Union[pyrogram.filters.Filter, "dispyro.filters.Filter"]

__all__ = ("AnyFilter", "Callback", "Handler", "Update")
