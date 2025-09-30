"""Dashboard container that swaps views based on the logged in user's role."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from ..auth import User
from ..database import db


class Dashboard(ttk.Frame):
    def __init__(self, master: tk.Misc, user: User) -> None:
        super().__init__(master)
        self.user = user
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._populate_tabs()

    def _populate_tabs(self) -> None:
        role = self.user.role
        self._add_sales_tab()
        if role in {"owner", "manager"}:
            self._add_inventory_tab()
            self._add_reports_tab()
            self._add_activity_tab()
        if role in {"owner", "manager", "staff"}:
            self._add_attendance_tab()
        if role == "owner":
            self._add_settings_tab()

    def _add_sales_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Sales & Billing")
        ttk.Label(frame, text="Sales terminal placeholder", font=("Helvetica", 14)).pack(pady=12)
        ttk.Label(
            frame,
            text=(
                "This prototype initialises the offline database and locks down access\n"
                "based on user roles. Extend this tab with the ordering interface,\n"
                "payment processing and receipt generation logic."
            ),
            justify=tk.CENTER,
        ).pack(pady=12)

    def _add_inventory_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Inventory")
        ttk.Label(frame, text="Inventory management placeholder", font=("Helvetica", 14)).pack(pady=12)
        ttk.Button(frame, text="View Items", command=self._show_inventory_records).pack(pady=8)
        self.inventory_list = tk.Listbox(frame, height=10)
        self.inventory_list.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

    def _show_inventory_records(self) -> None:
        self.inventory_list.delete(0, tk.END)
        rows = db.query(
            "SELECT name, sku, stock_quantity, expiration_date FROM inventory ORDER BY name"
        )
        for row in rows:
            expiry = row["expiration_date"] or "N/A"
            self.inventory_list.insert(
                tk.END, f"{row['name']} ({row['sku']}) - Stock: {row['stock_quantity']} - Exp: {expiry}"
            )

    def _add_reports_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Reports")
        ttk.Label(frame, text="Reports & Analytics placeholder", font=("Helvetica", 14)).pack(pady=12)
        ttk.Label(
            frame,
            text=(
                "Implement dashboards, loyalty insights, and offline charts in this tab."
            ),
        ).pack(pady=8)

    def _add_activity_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Activity Logs")
        ttk.Label(frame, text="Recent actions", font=("Helvetica", 14, "bold")).pack(pady=12)
        self.activity_list = tk.Listbox(frame, height=12)
        self.activity_list.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self._refresh_activity()

    def _refresh_activity(self) -> None:
        if not hasattr(self, "activity_list"):
            return
        self.activity_list.delete(0, tk.END)
        rows = db.query(
            "SELECT action, details, timestamp FROM activity_logs ORDER BY timestamp DESC LIMIT 20"
        )
        for row in rows:
            self.activity_list.insert(tk.END, f"[{row['timestamp']}] {row['action']} - {row['details']}")

    def _add_attendance_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Attendance")
        ttk.Label(frame, text="Attendance tracking placeholder", font=("Helvetica", 14)).pack(pady=12)
        ttk.Button(frame, text="Clock in", command=lambda: self._register_attendance("in")).pack(pady=6)
        ttk.Button(frame, text="Clock out", command=lambda: self._register_attendance("out")).pack(pady=6)

    def _register_attendance(self, action: str) -> None:
        timestamp = datetime.now().isoformat(timespec="seconds")
        if action == "in":
            db.execute(
                """
                INSERT OR IGNORE INTO attendance (staff_id, time_in, role)
                VALUES (?, ?, ?)
                """,
                (self.user.id, timestamp, self.user.role),
            )
        else:
            db.execute(
                """
                UPDATE attendance SET time_out = ?
                WHERE staff_id = ? AND date(time_in) = date('now')
                """,
                (timestamp, self.user.id),
            )
        self._log_action(f"Clocked {action}")

    def _add_settings_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")
        ttk.Label(frame, text="Store settings placeholder", font=("Helvetica", 14)).pack(pady=12)
        ttk.Label(frame, text="Use this area to configure themes, discounts, and receipt messages.").pack(pady=8)

    def _log_action(self, message: str) -> None:
        db.execute(
            "INSERT INTO activity_logs (user_id, action, details, timestamp) VALUES (?, ?, ?, datetime('now'))",
            (self.user.id, "attendance", message),
        )
        self._refresh_activity()
