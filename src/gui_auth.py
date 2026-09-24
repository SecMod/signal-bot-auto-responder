from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

APP_NAME = "SECMOD — SIGNAL BOT"
PBKDF2_ITERATIONS = 600_000


def _auth_path() -> Path:
    if os.name == "nt":
        base = Path(os.getenv("APPDATA", Path.home() / "AppData/Roaming"))
    else:
        base = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "secmod-signal-bot" / "gui_auth.json"


def _load_record() -> dict | None:
    try:
        with _auth_path().open("r", encoding="utf-8") as handle:
            record = json.load(handle)
        if not isinstance(record, dict):
            return None
        if not isinstance(record.get("salt"), str) or not isinstance(record.get("password_hash"), str):
            return None
        return record
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return None


def _write_record(password: str) -> None:
    path = _auth_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump({
            "version": 1,
            "algorithm": "pbkdf2-sha256",
            "iterations": PBKDF2_ITERATIONS,
            "salt": salt.hex(),
            "password_hash": digest.hex(),
        }, handle)
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def _verify(password: str, record: dict) -> bool:
    try:
        salt = bytes.fromhex(record["salt"])
        expected = bytes.fromhex(record["password_hash"])
        iterations = int(record.get("iterations", PBKDF2_ITERATIONS))
    except (KeyError, TypeError, ValueError):
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(actual, expected)


def _password_dialog(setup: bool) -> bool:
    result = {"ok": False}
    root = tk.Tk()
    root.title(APP_NAME)
    root.geometry("460x270" if setup else "460x230")
    root.resizable(False, False)
    root.configure(bg="#070a09")

    tk.Label(root, text="SECMOD", bg="#070a09", fg="#39ff88",
             font=("Segoe UI", 20, "bold")).pack(pady=(22, 2))
    tk.Label(root, text="SIGNAL BOT • AUTHENTICATION", bg="#070a09",
             fg="#8da99b", font=("Segoe UI", 9, "bold")).pack()
    tk.Label(
        root,
        text=("Create a password to protect this application."
              if setup else "Enter your password to unlock the Signal Bot."),
        bg="#070a09", fg="#f2fff8", font=("Segoe UI", 10)
    ).pack(pady=(18, 10))

    form = tk.Frame(root, bg="#070a09")
    form.pack(fill="x", padx=55)
    tk.Label(form, text="PASSWORD", bg="#070a09", fg="#8da99b").pack(anchor="w")
    password_var = tk.StringVar()
    password_entry = tk.Entry(
        form, textvariable=password_var, show="•", bg="#101815",
        fg="#f2fff8", insertbackground="#39ff88", relief="flat",
        font=("Segoe UI", 11)
    )
    password_entry.pack(fill="x", ipady=8, pady=(4, 10))

    confirm_var = tk.StringVar()
    if setup:
        tk.Label(form, text="CONFIRM PASSWORD", bg="#070a09", fg="#8da99b").pack(anchor="w")
        confirm_entry = tk.Entry(
            form, textvariable=confirm_var, show="•", bg="#101815",
            fg="#f2fff8", insertbackground="#39ff88", relief="flat",
            font=("Segoe UI", 11)
        )
        confirm_entry.pack(fill="x", ipady=8, pady=(4, 10))

    def unlock(event=None):
        password = password_var.get()
        if len(password) < 8:
            messagebox.showwarning("Password", "Use at least 8 characters.", parent=root)
            return
        if setup:
            if password != confirm_var.get():
                messagebox.showwarning("Password", "The passwords do not match.", parent=root)
                return
            try:
                _write_record(password)
            except OSError as exc:
                messagebox.showerror("Password", "Could not save password: " + str(exc), parent=root)
                return
        else:
            record = _load_record()
            if record is None or not _verify(password, record):
                password_var.set("")
                messagebox.showerror("Access denied", "Incorrect password.", parent=root)
                password_entry.focus_set()
                return
        result["ok"] = True
        root.destroy()

    def cancel():
        root.destroy()

    tk.Button(
        root,
        text="CREATE PASSWORD" if setup else "UNLOCK SIGNAL BOT",
        command=unlock, bg="#39ff88", fg="#070a09", relief="flat",
        font=("Segoe UI", 10, "bold"), padx=18, pady=9
    ).pack(pady=(4, 6))
    tk.Button(
        root, text="EXIT", command=cancel, bg="#131d18", fg="#f2fff8",
        relief="flat", padx=18, pady=6
    ).pack()

    root.bind("<Return>", unlock)
    root.protocol("WM_DELETE_WINDOW", cancel)
    password_entry.focus_set()
    root.mainloop()
    return result["ok"]


def require_gui_password() -> bool:
    return _password_dialog(setup=_load_record() is None)
