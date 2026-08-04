from collections.abc import Awaitable, Callable

FilterCallback = Callable[..., Awaitable[bool]]
