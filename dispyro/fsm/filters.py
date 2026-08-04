from dispyro.filters import Filter
from dispyro.types.contexts import UpdateContext

from .context import FSMContext
from .states import State


class StateFilter(Filter):
    """Filter that matches one or more FSM states.

    Pass ``None`` to match when no state is set (initial state).

    Example::

        @router.message(StateFilter(Form.waiting_name, Form.waiting_phone))
        async def handler(client, message): ...

        # Prefer using State directly for single-state matching:
        @router.message(Form.waiting_name)
        async def handler(client, message): ...
    """

    def __init__(self, *states: State | str | None) -> None:
        self._states: tuple[State | str | None, ...] = states
        self._states_as_str: set[str | None] = {str(s) if s is not None else None for s in states}

    async def __call__(self, context: UpdateContext) -> bool:
        fsm: FSMContext | None = context.data.get("state")

        if fsm is None:
            # Update has no identifiable sender — match only if None is listed.
            return None in self._states

        current = await fsm.get()
        return current in self._states_as_str
