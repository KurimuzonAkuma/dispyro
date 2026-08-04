from .filters import Filter
from .middlewares import BaseMiddleware
from .types import AnyFilter


class ProcessingContextHolder:
    def __init__(self, filters: AnyFilter | None = None) -> None:
        self.filters = Filter() & filters if filters else Filter()
        self.middlewares: list[BaseMiddleware] = []
        self.outer_middlewares: list[BaseMiddleware] = []

    def filter(self, filter: AnyFilter) -> None:
        self.filters &= filter

    def middleware(self, middleware: BaseMiddleware) -> None:
        self.middlewares.append(middleware)

    def outer_middleware(self, middleware: BaseMiddleware) -> None:
        self.outer_middlewares.append(middleware)
