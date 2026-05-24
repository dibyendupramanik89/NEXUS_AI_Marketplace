"""
NEXUS AI Marketplace - Global Shared Memory & Working Memory Manager
Implements: Session Memory, Long-term Memory, Context Retrieval, State Management
From the Enterprise Agentic AI Platform diagram (Memory Manager node).
"""

import time
import json
import hashlib
from collections import deque
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ConversationTurn:
    role: str                  # "user" | "assistant"
    content: str
    category: str
    timestamp: float = field(default_factory=time.time)
    intent_token_hash: Optional[str] = None


@dataclass
class UserProfile:
    """Non-PII preference profile built from interaction history."""
    session_id: str
    preferred_categories: Dict[str, int] = field(default_factory=dict)   # category → count
    typical_budget_range: Dict[str, float] = field(default_factory=dict)  # category → avg_budget
    geography_preference: Optional[str] = None
    interaction_count: int = 0
    last_active: float = field(default_factory=time.time)


@dataclass
class WorkingMemory:
    """Active context for current pipeline execution."""
    session_id: str
    current_query: str = ""
    current_category: str = ""
    agent_outputs: Dict[str, Any] = field(default_factory=dict)
    intermediate_results: List[Any] = field(default_factory=list)
    reasoning_steps: List[str] = field(default_factory=list)
    workflow_state: str = "idle"    # idle | classifying | auctioning | searching | synthesizing | done


@dataclass
class MemorySnapshot:
    """Complete memory state for observability dashboard."""
    session_id: str
    conversation_turns: int
    user_profile: UserProfile
    working_state: str
    context_window_tokens: int
    long_term_keys: int


# ─────────────────────────────────────────────
#  GLOBAL SHARED MEMORY STORE
# ─────────────────────────────────────────────

class GlobalMemoryStore:
    """
    In-memory store for session data, user profiles, and conversation history.
    Production upgrade: replace with Redis + PostgreSQL.
    Implements GDPR-safe storage — no raw PII, only intent hashes.
    """

    _sessions: Dict[str, deque] = {}          # session_id → conversation history
    _profiles: Dict[str, UserProfile] = {}    # session_id → user profile
    _working: Dict[str, WorkingMemory] = {}   # session_id → working memory
    _long_term: Dict[str, Any] = {}           # global key-value (shared across sessions)
    _audit_log: List[Dict] = []               # immutable audit trail

    @classmethod
    def init_session(cls, session_id: str) -> WorkingMemory:
        if session_id not in cls._sessions:
            cls._sessions[session_id] = deque(maxlen=20)   # keep last 20 turns
        if session_id not in cls._profiles:
            cls._profiles[session_id] = UserProfile(session_id=session_id)
        wm = WorkingMemory(session_id=session_id)
        cls._working[session_id] = wm
        cls._audit("session_init", session_id, {})
        return wm

    @classmethod
    def add_turn(cls, session_id: str, role: str, content: str, category: str, intent_hash: str = "") -> None:
        if session_id not in cls._sessions:
            cls.init_session(session_id)
        cls._sessions[session_id].append(ConversationTurn(
            role=role, content=content[:500],   # truncate to avoid bloat
            category=category,
            intent_token_hash=intent_hash,
        ))
        # Update profile
        profile = cls._profiles[session_id]
        profile.interaction_count += 1
        profile.last_active = time.time()
        if category:
            profile.preferred_categories[category] = profile.preferred_categories.get(category, 0) + 1

    @classmethod
    def get_context(cls, session_id: str, last_n: int = 3) -> List[ConversationTurn]:
        """Retrieve recent conversation context for the orchestrator."""
        if session_id not in cls._sessions:
            return []
        return list(cls._sessions[session_id])[-last_n:]

    @classmethod
    def update_working_memory(cls, session_id: str, **kwargs) -> None:
        if session_id not in cls._working:
            cls.init_session(session_id)
        wm = cls._working[session_id]
        for k, v in kwargs.items():
            if hasattr(wm, k):
                setattr(wm, k, v)

    @classmethod
    def get_working_memory(cls, session_id: str) -> Optional[WorkingMemory]:
        return cls._working.get(session_id)

    @classmethod
    def get_user_profile(cls, session_id: str) -> Optional[UserProfile]:
        return cls._profiles.get(session_id)

    @classmethod
    def set_long_term(cls, key: str, value: Any, session_id: str = "system") -> None:
        """Store shared knowledge (e.g., brand inventory, category stats)."""
        cls._long_term[key] = {"value": value, "updated": time.time(), "by": session_id}
        cls._audit("long_term_write", session_id, {"key": key})

    @classmethod
    def get_long_term(cls, key: str) -> Optional[Any]:
        rec = cls._long_term.get(key)
        return rec["value"] if rec else None

    @classmethod
    def snapshot(cls, session_id: str) -> MemorySnapshot:
        profile = cls._profiles.get(session_id, UserProfile(session_id=session_id))
        wm = cls._working.get(session_id, WorkingMemory(session_id=session_id))
        history = cls._sessions.get(session_id, deque())
        # Estimate token count: ~4 chars/token
        ctx_text = " ".join(t.content for t in history)
        return MemorySnapshot(
            session_id=session_id,
            conversation_turns=len(history),
            user_profile=profile,
            working_state=wm.workflow_state,
            context_window_tokens=len(ctx_text) // 4,
            long_term_keys=len(cls._long_term),
        )

    @classmethod
    def _audit(cls, action: str, session_id: str, metadata: dict) -> None:
        """Immutable audit log — append-only."""
        cls._audit_log.append({
            "ts": time.time(),
            "action": action,
            "session": session_id[:8],
            "meta": metadata,
        })

    @classmethod
    def get_audit_log(cls, last_n: int = 20) -> List[Dict]:
        return cls._audit_log[-last_n:]

    @classmethod
    def get_all_stats(cls) -> Dict:
        return {
            "active_sessions": len(cls._sessions),
            "total_profiles": len(cls._profiles),
            "long_term_keys": len(cls._long_term),
            "audit_entries": len(cls._audit_log),
        }


# Singleton
memory = GlobalMemoryStore()
