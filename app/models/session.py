import time
from collections import OrderedDict
from typing import Literal

from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(description="메시지 내용")
    timestamp: float = Field(default_factory=time.time)


class SessionHistory(BaseModel):
    session_id: str
    turns: list[ConversationTurn] = Field(default_factory=list)
    created_at: float = Field(default_factory=time.time)

    def add_turn(self, role: str, content: str) -> None:
        self.turns.append(ConversationTurn(role=role, content=content))

    def format_for_prompt(self, max_turns: int = 6) -> str:
        """Format recent turns as context string for LLM prompts."""
        recent = self.turns[-max_turns:]
        if not recent:
            return ""
        lines = []
        for turn in recent:
            label = "사용자" if turn.role == "user" else "시스템"
            lines.append(f"[{label}] {turn.content}")
        return "\n".join(lines)


class SessionStore:
    """In-memory LRU session store with TTL eviction."""

    def __init__(self, max_sessions: int = 100, ttl_seconds: int = 3600):
        self._store: OrderedDict[str, SessionHistory] = OrderedDict()
        self._max_sessions = max_sessions
        self._ttl_seconds = ttl_seconds

    def _evict_expired(self) -> None:
        now = time.time()
        expired = [
            sid
            for sid, session in self._store.items()
            if now - session.created_at > self._ttl_seconds
        ]
        for sid in expired:
            del self._store[sid]

    def get(self, session_id: str) -> SessionHistory | None:
        self._evict_expired()
        session = self._store.get(session_id)
        if session is not None:
            self._store.move_to_end(session_id)
        return session

    def create(self, session_id: str) -> SessionHistory:
        self._evict_expired()
        if len(self._store) >= self._max_sessions:
            self._store.popitem(last=False)
        session = SessionHistory(session_id=session_id)
        self._store[session_id] = session
        return session

    def get_or_create(self, session_id: str) -> SessionHistory:
        session = self.get(session_id)
        if session is None:
            session = self.create(session_id)
        return session

    def delete(self, session_id: str) -> bool:
        if session_id in self._store:
            del self._store[session_id]
            return True
        return False

    def __len__(self) -> int:
        return len(self._store)
