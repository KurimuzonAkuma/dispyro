import inspect
from functools import wraps
from inspect import Parameter
from typing import TYPE_CHECKING, Any, Callable, Dict, List, TypeVar

from pyrogram import Client
from pyrogram.filters import Filter as PyrogramFilter

if TYPE_CHECKING:
    from .filters import Filter as DispyroFilter

ReturnType = TypeVar("ReturnType")


class InterruptProcessing(Exception):
    """Exception to interrupt processing of update."""


def get_needed_kwargs(callable: Callable, **kwargs) -> Dict[str, Any]:
    """Helper function that fetches needed `kwargs`.
    Returns only needed kwargs in a form of a `dict`.
    """

    signature = inspect.signature(callable, follow_wrapped=False)
    kwnames: List[str] = []

    params = signature.parameters.copy()

    positional_args = list(params.keys())[:2]  # client and update are positional arguments

    for argname in positional_args:
        argparam = params[argname]

        if argparam.kind is Parameter.KEYWORD_ONLY:
            raise ValueError("client and update should be treated as positional arguments")

        params.pop(argname)

    for argname, argparam in params.items():
        kind = argparam.kind

        if kind is Parameter.POSITIONAL_ONLY:
            raise ValueError("only client and update should be positional arguments")

        elif kind in {Parameter.POSITIONAL_OR_KEYWORD, Parameter.KEYWORD_ONLY}:
            kwnames.append(argname)

        elif kind is Parameter.VAR_KEYWORD:
            return kwargs

    needed_kwargs = {k: v for k, v in kwargs.items() if k in kwnames}

    return needed_kwargs


def safe_call(callable: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
    """Helper function that makes new `callable` which feeds only needed `kwargs` to original."""

    @wraps(callable)
    def wrapper(*args, **kwargs) -> ReturnType:
        needed_kwargs = get_needed_kwargs(callable=callable, **kwargs)
        return callable(*args, **needed_kwargs)

    return wrapper


def adapt_pyrogram_filter(pyrogram_filter: PyrogramFilter) -> "DispyroFilter":
    """Wrap a Pyrogram filter into the dispyro Filter interface so it can be
    called with `context: UpdateContext` like all other dispyro filters."""
    # Local import to avoid circular dependency: filters → utils → filters.
    from .filters import Filter  # noqa: PLC0415
    from .types import Update

    async def callback(client: Client, update: Update) -> bool:
        return await pyrogram_filter(client, update)  # pyright: ignore [reportReturnType]

    return Filter(callback=callback)
