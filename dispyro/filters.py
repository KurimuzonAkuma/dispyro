from __future__ import annotations

from pyrogram import Client
from pyrogram.filters import Filter as PyrogramFilter

from .types import AnyFilter, Update
from .types.contexts import UpdateContext
from .types.signatures import FilterCallback
from .utils import adapt_pyrogram_filter, safe_call


class Filter:
    """Custom version of `Filter` type, which supports DI. This filters can be
    combined with default pyrogram filters.
    """

    async def _default_callback(self, _: Client, __: Update) -> bool:
        return True

    def __init__(self, callback: FilterCallback | None = None) -> None:
        self._unwrapped_callback = callback
        self._callback: FilterCallback = safe_call(callback or self._default_callback)

    async def __call__(self, context: UpdateContext) -> bool:
        return await self._callback(context.client, context.update, **context.data)

    def __invert__(self) -> InvertedFilter:
        return InvertedFilter(callback=self._unwrapped_callback)

    def __and__(self, other: AnyFilter) -> AndFilter:
        return AndFilter(left=self, right=other)

    def __or__(self, other: AnyFilter) -> OrFilter:
        return OrFilter(left=self, right=other)


class InvertedFilter(Filter):
    async def __call__(self, context: UpdateContext) -> bool:
        return not await super().__call__(context=context)

    def __invert__(self) -> Filter:
        return Filter(callback=self._unwrapped_callback)



class AndFilter(Filter):
    def __init__(self, left: AnyFilter, right: AnyFilter) -> None:
        if isinstance(left, PyrogramFilter):
            left = adapt_pyrogram_filter(left)

        if isinstance(right, PyrogramFilter):
            right = adapt_pyrogram_filter(right)

        self._left: Filter = left  # pyright: ignore [reportAssignmentType]
        self._right: Filter = right  # pyright: ignore [reportAssignmentType]

    async def __call__(self, context: UpdateContext) -> bool:
        left_value = await self._left(context=context)

        if not left_value:
            return False

        right_value = await self._right(context=context)

        return left_value and right_value


class OrFilter(Filter):
    def __init__(self, left: AnyFilter, right: AnyFilter) -> None:
        if isinstance(left, PyrogramFilter):
            left = adapt_pyrogram_filter(left)

        if isinstance(right, PyrogramFilter):
            right = adapt_pyrogram_filter(right)

        self._left: Filter = left  # pyright: ignore [reportAssignmentType]
        self._right: Filter = right  # pyright: ignore [reportAssignmentType]

    async def __call__(self, context: UpdateContext) -> bool:
        left_value = await self._left(context=context)

        if left_value:
            return True

        right_value = await self._right(context=context)

        return left_value or right_value

