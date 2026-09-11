"""
utils/storage.py

All JSON file I/O for the app lives here: user records, the admin
activity log, and the persisted login session. Plain dict/list-in,
dict/list-out functions (no classes) so UserRepository, AuthManager,
Session and the decorators can each import just what they need.

DATA_DIR/USERS_FILE/LOG_FILE are referenced as bare module globals
inside each function body (never captured into a local at import
time) so tests can monkeypatch them to a temp directory - see the
`auth_manager` fixture in tests/test_auth.py. The session file path
is derived from DATA_DIR at call time for the same reason, since
tests only ever redirect DATA_DIR itself.
"""

import json
import os

DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
LOG_FILE = os.path.join(DATA_DIR, "activity_log.json")


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def _read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path, data) -> None:
    _ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_users() -> dict:
    return _read_json(USERS_FILE, {})


def save_users(users: dict) -> None:
    _write_json(USERS_FILE, users)


def read_log() -> list:
    return _read_json(LOG_FILE, [])


def append_log(entry: dict) -> None:
    log = read_log()
    log.append(entry)
    _write_json(LOG_FILE, log)


def _session_file() -> str:
    return os.path.join(DATA_DIR, "session.json")


def load_session():
    """Returns the persisted logged-in username, or None."""
    data = _read_json(_session_file(), {})
    return data.get("username")


def save_session(username: str) -> None:
    _write_json(_session_file(), {"username": username})


def clear_session() -> None:
    path = _session_file()
    if os.path.exists(path):
        os.remove(path)
