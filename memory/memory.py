"""memory.py — Dual-layer SQLite memory for Kira.

Two storage tiers:
  short_memory  — recent conversation turns (rolling window, auto-pruned)
  long_memory   — durable facts extracted by the assembler (permanent)
"""

import os
import sqlite3
from config import DB_PATH, MEMORY_LIMIT

# Ensure data directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_cursor = _conn.cursor()

# Short-term: conversation turns
_cursor.execute("""
CREATE TABLE IF NOT EXISTS short_memory (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    role    TEXT    NOT NULL DEFAULT 'agent',
    content TEXT    NOT NULL,
    ts      DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Long-term: durable facts only
_cursor.execute("""
CREATE TABLE IF NOT EXISTS long_memory (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    fact    TEXT    NOT NULL UNIQUE,
    ts      DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

_conn.commit()


# ---------------------------------------------------------------------------
# Short-term memory (conversation context)
# ---------------------------------------------------------------------------

def save_memory(content: str, role: str = "agent") -> None:
    """Persist a conversation turn (user or agent)."""
    _cursor.execute(
        "INSERT INTO short_memory (role, content) VALUES (?, ?)",
        (role, content),
    )
    _conn.commit()
    _prune_short_memory()


def get_memory(limit: int = MEMORY_LIMIT) -> list[str]:
    """Return the N most recent short-term turns, oldest-first, with role labels."""
    _cursor.execute(
        "SELECT role, content FROM short_memory ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = _cursor.fetchall()
    return [f"[{role.upper()}] {content}" for role, content in reversed(rows)]


def _prune_short_memory(keep: int = 50) -> None:
    """Auto-prune short_memory to the last `keep` rows."""
    _cursor.execute("""
        DELETE FROM short_memory
        WHERE id NOT IN (
            SELECT id FROM short_memory ORDER BY id DESC LIMIT ?
        )
    """, (keep,))
    _conn.commit()


def clear_memory() -> None:
    """Wipe all short-term memory entries."""
    _cursor.execute("DELETE FROM short_memory")
    _conn.commit()


# ---------------------------------------------------------------------------
# Long-term memory (durable facts)
# ---------------------------------------------------------------------------

def save_fact(fact: str) -> None:
    """Persist a durable fact. Silently ignores duplicates (UNIQUE constraint)."""
    try:
        _cursor.execute("INSERT INTO long_memory (fact) VALUES (?)", (fact,))
        _conn.commit()
    except sqlite3.IntegrityError:
        pass  # Duplicate fact — skip


def get_facts(limit: int = 10) -> list[str]:
    """Return the N most recently stored facts."""
    _cursor.execute(
        "SELECT fact FROM long_memory ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    return [row[0] for row in _cursor.fetchall()]


def get_full_context(short_limit: int = MEMORY_LIMIT, fact_limit: int = 5) -> str:
    """
    Build a combined context string for LLM injection:
      - Recent conversation turns (short-term)
      - Relevant long-term facts
    """
    parts = []

    facts = get_facts(fact_limit)
    if facts:
        parts.append("## Long-term Facts\n" + "\n".join(f"• {f}" for f in facts))

    turns = get_memory(short_limit)
    if turns:
        parts.append("## Recent Conversation\n" + "\n".join(turns))

    return "\n\n".join(parts) if parts else ""


def clear_all() -> None:
    """Wipe both memory tiers."""
    _cursor.execute("DELETE FROM short_memory")
    _cursor.execute("DELETE FROM long_memory")
    _conn.commit()