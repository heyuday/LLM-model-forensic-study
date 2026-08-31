"""SQLite cache for batch API responses."""

import hashlib
import json
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent / "cache.db"


def _get_conn(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """CREATE TABLE IF NOT EXISTS batch_cache (
            key TEXT PRIMARY KEY,
            params_json TEXT NOT NULL,
            responses_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    return conn


def make_batch_key(
    model: str,
    messages_list: list,
    n_samples: int,
    **kwargs,
) -> str:
    """Hash the batch config into a cache key."""
    payload = {
        "model": model,
        "messages_list": messages_list,
        "n_samples": n_samples,
        **kwargs,
    }
    dumped = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(dumped.encode()).hexdigest()


def load_batch(key: str, db_path: Path = DEFAULT_DB_PATH) -> list[dict] | None:
    """Load cached batch responses. Returns None on cache miss."""
    conn = _get_conn(db_path)
    row = conn.execute(
        "SELECT responses_json FROM batch_cache WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    if row is None:
        return None
    return json.loads(row[0])


def save_batch(key: str, params: dict, responses: list[dict], db_path: Path = DEFAULT_DB_PATH) -> None:
    """Save batch responses to cache."""
    conn = _get_conn(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO batch_cache (key, params_json, responses_json) VALUES (?, ?, ?)",
        (key, json.dumps(params, default=str), json.dumps(responses, default=str)),
    )
    conn.commit()
    conn.close()
