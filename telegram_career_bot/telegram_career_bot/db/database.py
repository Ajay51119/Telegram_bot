"""
SQLite persistence for user profiles.

This is intentionally separate from LangGraph's own MemorySaver checkpointer
(graph/build.py), which only tracks per-chat conversation history. This DB is
the durable source of truth for who the person is and what we know about
their career profile, and it survives bot restarts (MemorySaver does not).
"""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "bot.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id        TEXT UNIQUE NOT NULL,
    username           TEXT,
    email              TEXT,
    phone              TEXT,
    profile            TEXT,
    designation        TEXT,
    skills             TEXT,
    resume_text        TEXT,
    onboarding_stage   TEXT DEFAULT 'new',
    pending_intent     TEXT,
    pending_extraction TEXT,
    token_limit        INTEGER DEFAULT 100,
    tokens_used        INTEGER DEFAULT 0,
    total_interactions INTEGER DEFAULT 0,
    status             TEXT DEFAULT 'active',
    last_active        TEXT DEFAULT CURRENT_TIMESTAMP,
    created_at         TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at         TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

MIGRATIONS = [
    ("phone", "phone TEXT"),
    ("token_limit", "token_limit INTEGER DEFAULT 100"),
    ("tokens_used", "tokens_used INTEGER DEFAULT 0"),
    ("total_interactions", "total_interactions INTEGER DEFAULT 0"),
    ("status", "status TEXT DEFAULT 'active'"),
    ("last_active", "last_active TEXT"),
]

_JSON_COLUMNS = {"skills", "pending_extraction"}


@contextmanager
def _get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(SCHEMA)
        existing_columns = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
        for column_name, column_sql in MIGRATIONS:
            if column_name not in existing_columns:
                conn.execute(f"ALTER TABLE users ADD COLUMN {column_sql}")


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for col in _JSON_COLUMNS:
        raw = d.get(col)
        if raw:
            try:
                d[col] = json.loads(raw)
            except (TypeError, ValueError):
                d[col] = None
        else:
            d[col] = [] if col == "skills" else None
    d["name"] = d.get("username") or d.get("name")
    d["user_id"] = d.get("id")
    d["phone"] = d.get("phone")
    d["resume_filename"] = None
    if d.get("token_limit") is None:
        d["token_limit"] = 100
    if d.get("tokens_used") is None:
        d["tokens_used"] = 0
    if d.get("total_interactions") is None:
        d["total_interactions"] = 0
    if d.get("status") is None:
        d["status"] = "active"
    return d


def get_user(telegram_id: str) -> Optional[dict]:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()
        return _row_to_dict(row) if row else None


def create_user(
    telegram_id: str,
    username: Optional[str] = None,
    email: Optional[str] = None,
    onboarding_stage: str = "new",
) -> dict:
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO users (telegram_id, username, email, onboarding_stage) VALUES (?, ?, ?, ?)",
            (telegram_id, username, email, onboarding_stage),
        )
    return get_user(telegram_id)


def update_user(telegram_id: str, **fields: Any) -> dict:
    """Update arbitrary columns for a user. Lists and dicts are JSON-encoded automatically."""
    if not fields:
        return get_user(telegram_id)

    set_clauses = ["updated_at = CURRENT_TIMESTAMP"]
    values = []
    for key, value in fields.items():
        if key in _JSON_COLUMNS and value is not None and not isinstance(value, str):
            value = json.dumps(value)
        set_clauses.append(f"{key} = ?")
        values.append(value)
    values.append(telegram_id)

    with _get_conn() as conn:
        conn.execute(
            f"UPDATE users SET {', '.join(set_clauses)} WHERE telegram_id = ?", values
        )
    return get_user(telegram_id)


def get_or_create_user(telegram_id: str) -> dict:
    user = get_user(telegram_id)
    if user is None:
        user = create_user(telegram_id)
    return user


def consume_tokens(telegram_id: str, amount: int = 1) -> tuple[bool, dict]:
    user = get_or_create_user(telegram_id)
    token_limit = user.get("token_limit") or 100
    tokens_used = int(user.get("tokens_used") or 0)

    if tokens_used >= token_limit:
        update_user(telegram_id, status="limit_reached")
        return False, get_user(telegram_id)

    new_tokens = tokens_used + amount
    status = "limit_reached" if new_tokens >= token_limit else "active"
    update_user(
        telegram_id,
        tokens_used=new_tokens,
        total_interactions=(int(user.get("total_interactions") or 0) + 1),
        status=status,
    )
    return True, get_user(telegram_id)


def set_token_limit_for_all(token_limit: int) -> int:
    with _get_conn() as conn:
        cursor = conn.execute(
            "UPDATE users SET token_limit = ?, status = CASE WHEN tokens_used >= ? THEN 'limit_reached' ELSE 'active' END",
            (token_limit, token_limit),
        )
        return cursor.rowcount


def get_users(page: int = 1, limit: int = 20, filters: Optional[dict] = None) -> dict:
    page = max(1, int(page))
    limit = max(1, int(limit))
    filters = filters or {}

    where_clauses = []
    values: list[Any] = []

    search = (filters.get("search") or "").strip()
    if search:
        where_clauses.append("(username LIKE ? OR email LIKE ? OR telegram_id LIKE ?)")
        like = f"%{search}%"
        values.extend([like, like, like])

    onboarding_stage = filters.get("onboarding_stage")
    if onboarding_stage:
        where_clauses.append("onboarding_stage = ?")
        values.append(onboarding_stage)

    status = filters.get("status")
    if status:
        where_clauses.append("status = ?")
        values.append(status)

    min_tokens = filters.get("min_tokens")
    if min_tokens is not None:
        where_clauses.append("tokens_used >= ?")
        values.append(int(min_tokens))

    sort_by = filters.get("sort_by", "updated_at")
    order = filters.get("order", "desc")
    allowed_sort = {
        "name": "username",
        "email": "email",
        "tokens_used": "tokens_used",
        "total_interactions": "total_interactions",
        "last_active": "updated_at",
        "created_at": "created_at",
        "updated_at": "updated_at",
    }
    sort_column = allowed_sort.get(sort_by, "updated_at")
    sort_order = "ASC" if str(order).lower() == "asc" else "DESC"

    query = "SELECT * FROM users"
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
    query += f" ORDER BY {sort_column} {sort_order}"

    with _get_conn() as conn:
        total = conn.execute(
            f"SELECT COUNT(*) AS c FROM ({query})", values
        ).fetchone()["c"]
        rows = conn.execute(
            query + " LIMIT ? OFFSET ?",
            values + [limit, (page - 1) * limit],
        ).fetchall()

    users = [_row_to_dict(row) for row in rows]
    total_pages = max(1, (total + limit - 1) // limit) if total else 1
    return {"users": users, "total": total, "page": page, "limit": limit, "total_pages": total_pages}


def search_users(query: str, field: str = "name") -> list[dict]:
    query = (query or "").strip()
    if not query:
        return []

    field = field.lower()
    if field == "email":
        sql = "SELECT * FROM users WHERE email LIKE ? ORDER BY updated_at DESC LIMIT 20"
        value = f"%{query}%"
    else:
        sql = "SELECT * FROM users WHERE username LIKE ? OR telegram_id LIKE ? ORDER BY updated_at DESC LIMIT 20"
        value = f"%{query}%"
        values = (value, value)
    with _get_conn() as conn:
        rows = conn.execute(sql, values if field != "email" else (value,)).fetchall()
    return [_row_to_dict(row) for row in rows]


def get_stats() -> dict:
    with _get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        total_tokens_used = conn.execute("SELECT COALESCE(SUM(tokens_used), 0) AS c FROM users").fetchone()["c"]
        active_users_today = conn.execute(
            "SELECT COUNT(*) AS c FROM users WHERE date(updated_at) = date('now')"
        ).fetchone()["c"]
        new_users_this_month = conn.execute(
            "SELECT COUNT(*) AS c FROM users WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')"
        ).fetchone()["c"]
        most_active_rows = conn.execute(
            "SELECT username, telegram_id, tokens_used, total_interactions FROM users ORDER BY tokens_used DESC LIMIT 5"
        ).fetchall()

    most_active_users = [
        {
            "name": row["username"] or row["telegram_id"],
            "tokens_used": row["tokens_used"],
            "interactions": row["total_interactions"],
        }
        for row in most_active_rows
    ]
    avg_tokens_per_user = round(total_tokens_used / total_users, 2) if total_users else 0
    return {
        "total_users": total_users,
        "total_tokens_used": total_tokens_used,
        "avg_tokens_per_user": avg_tokens_per_user,
        "active_users_today": active_users_today,
        "new_users_this_month": new_users_this_month,
        "onboarding_completion_rate": 0.0,
        "user_growth_trend": 0.0,
        "most_active_users": most_active_users,
    }
