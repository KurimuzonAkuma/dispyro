from collections import defaultdict
from collections.abc import AsyncGenerator
from dataclasses import dataclass, field
from typing import Any

from pyrogram import Client

import dispyro
from dispyro.enums import MiddlewareState

from .union_types import Update

MiddlewaresContext = dict["dispyro.middlewares.BaseMiddleware", "MiddlewareContext"]


@dataclass
class MiddlewareContext:
    state: MiddlewareState = MiddlewareState.UNACTIVE
    iterable: AsyncGenerator[Any, Any] | None = None


@dataclass
class UpdateContext:
    client: Client
    update: Update
    data: dict[str, Any]
    _middlewares_context: MiddlewaresContext = field(default_factory=lambda: defaultdict(MiddlewareContext))
    # Indicates whether any handler was triggered during processing of this
    # specific update. Stored here (not on Handler/Router instances) to avoid
    # state sharing across concurrent update processing tasks.
    handler_triggered: bool = False
    router_triggered: bool = False
