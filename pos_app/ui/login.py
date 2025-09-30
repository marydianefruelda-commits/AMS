"""Tkinter login window for Kapipang Blends POS."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from ..auth import verify_credentials


class LoginWindow(tk.Toplevel):
    def __init__(self, master: tk.Misc, on_success) -> None:
        super().__init__(master)
        self.title("Kapipang Blends POS - Login")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.on_success = on_success

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self._build_ui()

    def _build_ui(self) -> None:
        container = tk.Frame(self, padx=24, pady=24)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Welcome to Kapipang Blends", font=("Helvetica", 16, "bold")).pack(pady=(0, 12))

        form = tk.Frame(container)
        form.pack(fill=tk.X)

        tk.Label(form, text="Username").grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(form, textvariable=self.username_var).grid(row=1, column=0, sticky="ew", pady=(0, 8))

        tk.Label(form, text="Password").grid(row=2, column=0, sticky="w", pady=4)
        tk.Entry(form, textvariable=self.password_var, show="*").grid(row=3, column=0, sticky="ew", pady=(0, 12))

        form.columnconfigure(0, weight=1)

        tk.Button(container, text="Login", command=self._attempt_login, width=20).pack(pady=(8, 0))

    def _attempt_login(self) -> None:
        username = self.username_var.get().strip()
        password = self.password_var.get()
        if not username or not password:
            messagebox.showerror("Missing information", "Please enter both username and password.")
            return

        user = verify_credentials(username, password)
        if not user:
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return

        messagebox.showinfo("Success", f"Logged in as {user.role.title()}.")
        self.on_success(user)
        self.destroy()

    def _on_close(self) -> None:
        if messagebox.askokcancel("Quit", "Do you want to exit the POS system?"):
            self.master.destroy()
