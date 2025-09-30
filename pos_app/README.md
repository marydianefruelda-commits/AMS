# Kapipang Blends POS Prototype

This repository now includes a Python/Tkinter prototype that lays the
foundation for the offline Kapipang Blends point-of-sale (POS) system.
It focuses on two key objectives:

1. Prepare the complete SQLite schema required by the specification.
2. Provide a role-aware Tkinter shell that can be expanded into the full
   experience (sales terminal, inventory, analytics, attendance, etc.).

## Features

- **Offline SQLite database** with the required tables (users, inventory,
  sales, sale items, customers, attendance, activity logs, and store
  settings).
- **Role-based authentication** with password hashing. Default
  credentials are created on first run (owner/manager/staff with
  `*123` passwords). As soon as a user logs in, their password is
  upgraded to a salted SHA-256 hash stored in the database.
- **Tkinter interface** featuring a login window and dashboard. The
  dashboard dynamically enables tabs depending on the logged-in user's
  role to demonstrate the access model.
- **Attendance logging** prototype which records clock in/out actions and
  pushes them to the activity log.
- **Activity log viewer** available to the owner and manager roles.

## Running the prototype

```bash
python -m pos_app.main
```

The first execution will create the `kapipang_pos.db` SQLite database in
`pos_app/`. Subsequent runs will reuse the same data file.

## Next steps

This code purposefully keeps the UI lightweight so the business logic
can be iteratively implemented. Suggested areas to build next:

- Flesh out the Sales & Billing tab with product buttons, order tables,
  payment handling, loyalty redemptions, and receipt printing.
- Extend the Inventory tab to add/edit products, trigger low stock
  notifications, and manage expiration tracking.
- Implement analytics charts (Matplotlib) and report export tools.
- Finalise customer loyalty workflows and birthday promotions.
- Harden security (password reset flows, void password management, idle
  timeout enforcement).

The provided structure should help accelerate the remaining work while
keeping the application fully offline-ready.
