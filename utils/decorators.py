"""
decorators.py
Custom decorators demonstrating a key OOP/functional Python technique:
  - login_required: blocks a CLI action unless a user session is active
  - admin_required: blocks a CLI action unless the active user is an admin
  - log_action: writes a line to data/activity.log every time a decorated
    function runs (simple audit trail)

These decorate the "command handler" functions in cli/commands, each of
which receives a `session` object as its first argument.
"""

import functools
import os
from datetime import datetime

from utils import storage


def _log_path() -> str:
    # Resolved at call time (not import time) so tests that redirect
    # storage.DATA_DIR to a temp folder never touch the real activity.log.
    return os.path.join(storage.DATA_DIR, "activity.log")


def login_required(func):
    """Ensure a user is logged in (session.current_user is set) before running func."""
    @functools.wraps(func)
    def wrapper(session, *args, **kwargs):
        if session.current_user is None:
            print("You must be logged in to do that. Try `login` first.")
            return None
        return func(session, *args, **kwargs)
    return wrapper


def admin_required(func):
    """Ensure the logged-in user has the 'admin' role."""
    @functools.wraps(func)
    def wrapper(session, *args, **kwargs):
        if session.current_user is None:
            print("You must be logged in to do that.")
            return None
        if not session.current_user.is_admin:
            print("Permission denied: this action requires an admin role.")
            return None
        return func(session, *args, **kwargs)
    return wrapper


def log_action(func):
    """Append a timestamped audit-trail line every time the decorated action runs."""
    @functools.wraps(func)
    def wrapper(session, *args, **kwargs):
        result = func(session, *args, **kwargs)
        who = session.current_user.username if session.current_user else "anonymous"
        try:
            with open(_log_path(), "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} | {who} | {func.__name__}\n")
        except OSError:
            pass  # logging should never crash the app
        return result
    return wrapper
