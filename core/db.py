import sqlite3
from pathlib import Path
from typing import Optional, Any, Dict, Tuple, List

class DB:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self):
        with self._connect() as con:
            cur = con.cursor()
            # users
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                user_hash TEXT UNIQUE,
                created_at INTEGER,
                last_active INTEGER,
                banned INTEGER DEFAULT 0
            );""")

            con.commit()

    # ——— users ———
    def get_all_users(self) -> list:
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
        
    def count_users(self) -> int:
        with self._connect() as con:
            cur = con.cursor()
            return cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    def get_users_page(self, limit: int, offset: int):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM users ORDER BY created_at ASC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            return cur.fetchall()

    def get_user(self, user_id: int) -> Optional[sqlite3.Row]:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
            return cur.fetchone()

    def upsert_user(self, user_id: int, username: Optional[str], full_name: str, user_hash: str, now_ts: int) -> sqlite3.Row:
        with self._connect() as con:
            cur = con.cursor()
            existing = self.get_user(user_id)
            if existing:
                cur.execute("""UPDATE users SET username=?, full_name=?, last_active=?
                               WHERE user_id=?""", (username, full_name, now_ts, user_id))
            else:
                cur.execute("""INSERT INTO users (user_id, username, full_name, user_hash, created_at, last_active)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                            (user_id, username, full_name, user_hash, now_ts, now_ts))
            con.commit()
        return self.get_user(user_id)

    def set_ban(self, user_id: int, banned: bool):
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET banned=? WHERE user_id=?", (1 if banned else 0, user_id))
            con.commit()

    def find_user_by_any(self, key: str) -> Optional[sqlite3.Row]:
        with self._connect() as con:
            cur = con.cursor()
            if key.isdigit():
                cur.execute("SELECT * FROM users WHERE user_id=?", (int(key),))
            elif key.startswith('@'):
                cur.execute("SELECT * FROM users WHERE username=?", (key[1:],))
            else:
                cur.execute("SELECT * FROM users WHERE user_hash=?", (key,))
            return cur.fetchone()

    def stats_for_user(self, user_id: int) -> Dict[str, Any]:
        with self._connect() as con:
            cur = con.cursor()
            cur.execute("SELECT created_at, last_active, user_hash, username, full_name FROM users WHERE user_id=?", (user_id,))
            row = cur.fetchone()
            return {
                "created_at": row["created_at"] if row else None,
                "last_active": row["last_active"] if row else None,
                "user_hash": row["user_hash"] if row else None,
                "username": row["username"] if row else None,
                "full_name": row["full_name"] if row else None,
            }
