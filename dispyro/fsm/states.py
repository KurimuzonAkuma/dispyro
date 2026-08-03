from typing import TYPE_CHECKING

from ..filters import Filter
from ..types.contexts import UpdateContext

if TYPE_CHECKING:
    from .context import FSMContext


class State(Filter):
    """A single FSM state. Inherits Filter so it can be used directly as a
    filter in handler decorators and combined with other filters via &/|/~.

    Example::

        class Form(StatesGroup):
            waiting_name = State()
            waiting_phone = State()

        @router.message(Form.waiting_name)
        async def handle_name(client, message, state: FSMContext):
            await state.set(Form.waiting_phone)
    """

    _group: "type[StatesGroup]"
    _name: str

    def __init__(self) -> None:
        # Do not call Filter.__init__ — we override __call__ completely
        # and don't need a callback. Operators &/|/~ are inherited from Filter.
        pass

    async def __call__(self, context: UpdateContext) -> bool:
        fsm: "FSMContext | None" = context.data.get("state")
        if fsm is None:
            return False
        current = await fsm.get()
        return current == str(self)

    def __str__(self) -> str:
        return f"{self._group.__name__}:{self._name}"

    def __repr__(self) -> str:
        return f"<State {self}>"


class StatesGroup:
    """Base class for defining FSM state groups.

    Example::

        class Form(StatesGroup):
            waiting_name = State()
            waiting_phone = State()
    """

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        for name, value in cls.__dict__.items():
            if isinstance(value, State):
                value._group = cls
                value._name = name
