"""Database utilities for Kapipang Blends POS system.

This module centralises creation of the SQLite database and exposes
helpers for querying data across the application.  Everything is kept
self-contained so the application can run entirely offline.
"""
from __future__ import annotations

import contextlib
import sqlite3
from pathlib import Path
from typing import Generator, Iterable

DB_PATH = Path(__file__).with_name("kapipang_pos.db")


class DatabaseManager:
    """Handle connections and schema management for the POS system."""

    def __init__(self, path: Path | str | None = None) -> None:
        self.db_path = Path(path) if path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialise()

    def _initialise(self) -> None:
        with self.get_connection() as conn:
            self._create_tables(conn)
            self._ensure_default_users(conn)

    @staticmethod
    def _create_tables(conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        cursor.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('owner', 'manager', 'staff'))
            );

            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                loyalty_points INTEGER DEFAULT 0,
                birthday TEXT,
                favorites TEXT
            );

            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                sku TEXT UNIQUE NOT NULL,
                cogs REAL NOT NULL,
                selling_price REAL NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                expiration_date TEXT,
                low_stock_threshold INTEGER DEFAULT 0,
                UNIQUE(name, sku)
            );

            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                total_amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                discount REAL DEFAULT 0,
                loyalty_points_used INTEGER DEFAULT 0,
                loyalty_points_earned INTEGER DEFAULT 0,
                feedback_qr TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );

            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                inventory_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (inventory_id) REFERENCES inventory(id)
            );

            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_id INTEGER NOT NULL,
                time_in TEXT NOT NULL,
                time_out TEXT,
                role TEXT NOT NULL,
                UNIQUE(staff_id, date(time_in)),
                FOREIGN KEY (staff_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK(id = 1),
                store_name TEXT DEFAULT 'Kapipang Blends',
                theme TEXT DEFAULT 'light',
                discount_presets TEXT,
                loyalty_points_ratio REAL DEFAULT 0.01,
                tax_rate REAL DEFAULT 0.0,
                service_charge REAL DEFAULT 0.0,
                receipt_footer TEXT DEFAULT 'Thank you for visiting Kapipang Blends!',
                idle_timeout INTEGER DEFAULT 300
            );
            """
        )
        conn.commit()

    @staticmethod
    def _ensure_default_users(conn: sqlite3.Connection) -> None:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        (count,) = cursor.fetchone()
        if count:
            return

        cursor.executemany(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            [
                ("owner", "owner123", "owner"),
                ("manager", "manager123", "manager"),
                ("staff", "staff123", "staff"),
            ],
        )
        cursor.execute("INSERT OR IGNORE INTO settings (id) VALUES (1)")
        conn.commit()

    @contextlib.contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def query(self, query: str, params: Iterable | None = None) -> list[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            return cursor.fetchall()

    def execute(self, query: str, params: Iterable | None = None) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            conn.commit()


db = DatabaseManager()
