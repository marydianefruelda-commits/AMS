"""Authentication helpers for the Kapipang Blends POS system."""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .database import db, DatabaseManager


@dataclass
class User:
    id: int
    username: str
    role: str


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode()).hexdigest()


def create_user(username: str, password: str, role: str, *, manager: DatabaseManager | None = None) -> None:
    if role not in {"owner", "manager", "staff"}:
        raise ValueError("Invalid role")

    manager = manager or db
    salt = secrets.token_hex(16)
    hashed = _hash_password(password, salt)
    manager.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, f"{salt}${hashed}", role),
    )


def verify_credentials(username: str, password: str, *, manager: DatabaseManager | None = None) -> Optional[User]:
    manager = manager or db
    with manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return None

        stored = row["password"]
        if "$" not in stored:
            # Legacy plain-text password, upgrade on the fly
            hashed = _hash_password(password, salt := secrets.token_hex(16))
            cursor.execute(
                "UPDATE users SET password = ? WHERE id = ?",
                (f"{salt}${hashed}", row["id"]),
            )
            conn.commit()
            return User(id=row["id"], username=row["username"], role=row["role"])

        salt, digest = stored.split("$", 1)
        if _hash_password(password, salt) != digest:
            return None
        return User(id=row["id"], username=row["username"], role=row["role"])


def log_activity(user: User, action: str, details: str = "", *, manager: DatabaseManager | None = None) -> None:
    manager = manager or db
    timestamp = datetime.now().isoformat(timespec="seconds")
    manager.execute(
        "INSERT INTO activity_logs (user_id, action, details, timestamp) VALUES (?, ?, ?, ?)",
        (user.id, action, details, timestamp),
    )


def ensure_default_passwords_hashed() -> None:
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users")
        updates: list[tuple[str, int]] = []
        for row in cursor.fetchall():
            if "$" in row["password"]:
                continue
            salt = secrets.token_hex(16)
            updates.append((f"{salt}${_hash_password(row['password'], salt)}", row["id"]))
        if updates:
            cursor.executemany("UPDATE users SET password = ? WHERE id = ?", updates)
            conn.commit()
