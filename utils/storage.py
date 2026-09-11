"""
utils/storage.py

JSON persistence, in two shapes used across the app:
  - load_users()/save_users(): the dict-keyed store UserRepository is
    built against (username -> user dict).
  - load_json()/save_json(): a generic list-keyed store for anything
    else that persists a list of records (projects, tasks, the
    session pointer).
DATA_DIR/USERS_FILE/LOG_FILE are module attributes (not hardcoded
inline) so tests can monkeypatch them to a temp directory and have
every reader/writer pick that up immediately - no test ever touches
the real data/ folder.

A missing file starts empty instead of crashing; a corrupted file is
reported and treated the same way. Writes go through a temp file +
os.replace so a crash mid-write never leaves a half-written file.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
LOG_FILE = os.path.join(DATA_DIR, "activity_log.json")


def _read(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return json.loads(content) if content else default
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[warning] Could not read {path} ({exc}); starting fresh.")
        return default


def _write(path, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


def load_users() -> dict:
    return _read(USERS_FILE, {})


def save_users(users: dict) -> None:
    _write(USERS_FILE, users)


def log_activity(who: str, action: str) -> None:
    try:
        entries = _read(LOG_FILE, [])
        entries.append({"who": who, "action": action, "at": datetime.now().isoformat()})
        _write(LOG_FILE, entries)
    except OSError:
        pass  # audit logging should never crash the app


def load_log() -> list:
    return _read(LOG_FILE, [])


def load_json(filename: str):
    return _read(os.path.join(DATA_DIR, filename), [])


def save_json(filename: str, data) -> None:
    _write(os.path.join(DATA_DIR, filename), data)
