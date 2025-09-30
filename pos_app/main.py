"""Entry point for the Kapipang Blends POS prototype."""
from __future__ import annotations

import tkinter as tk
from .auth import User, ensure_default_passwords_hashed, log_activity
from .ui.dashboard import Dashboard
from .ui.login import LoginWindow


class POSApplication(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Kapipang Blends POS")
        self.geometry("900x600")
        self.minsize(900, 600)
        self.style = None
        self.user: User | None = None

        ensure_default_passwords_hashed()
        self.after(0, self._show_login)

    def _show_login(self) -> None:
        self.withdraw()
        LoginWindow(self, self._on_login_success)

    def _on_login_success(self, user: User) -> None:
        self.user = user
        self.deiconify()
        self._render_dashboard()
        log_activity(user, "login", "User signed in")

    def _render_dashboard(self) -> None:
        for child in self.winfo_children():
            child.destroy()
        if not self.user:
            return
        dashboard = Dashboard(self, self.user)
        dashboard.pack(fill=tk.BOTH, expand=True)


def main() -> None:
    POSApplication().mainloop()


if __name__ == "__main__":
    main()
