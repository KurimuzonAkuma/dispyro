from __future__ import annotations

from collections.abc import Callable
from typing import Any, Concatenate

from pyrogram import Client
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    InlineQuery,
    Message,
    Poll,
    User,
)
from typing_extensions import ParamSpec

import dispyro

Callback = Callable[..., Any]
Decorator = Callable[[Callback], Callback]

P = ParamSpec("P")

CallbackQueryHandlerCallback = Callable[Concatenate[Client, CallbackQuery, P], Any]
ChatMemberUpdatedHandlerCallback = Callable[Concatenate[Client, ChatMemberUpdated, P], Any]
ChosenInlineResultHandlerCallback = Callable[Concatenate[Client, ChosenInlineResult, P], Any]
DeletedMessagesHandlerCallback = Callable[Concatenate[Client, list[Message], P], Any]
EditedMessageHandlerCallback = Callable[Concatenate[Client, Message, P], Any]
InlineQueryHandlerCallback = Callable[Concatenate[Client, InlineQuery, P], Any]
MessageHandlerCallback = Callable[Concatenate[Client, Message, P], Any]
PollHandlerCallback = Callable[Concatenate[Client, Poll, P], Any]
RawUpdateHandlerCallback = Callable[Concatenate[Client, dispyro.types.PackedRawUpdate, P], Any]
UserStatusHandlerCallback = Callable[Concatenate[Client, User, P], Any]
