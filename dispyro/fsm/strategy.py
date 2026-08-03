from enum import Enum, auto

class FSMStrategy(Enum):
    """
    FSM state resolution strategy.
    
    - USER_IN_CHAT (default): State is bound to user and chat. In PM, it matches inline queries. In groups, it's isolated.
    - GLOBAL_USER: State is bound to user only. State matches across all chats and inline queries.
    - CHAT_ONLY: State is bound to chat only. All users in the same chat share the same state.
    """
    USER_IN_CHAT = auto()
    GLOBAL_USER = auto()
    CHAT_ONLY = auto()
