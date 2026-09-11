"""
utils/decorators.py

Cross-cutting concerns for CLI command functions, kept out of the
business logic itself:
  - login_required: blocks a command unless a user session is active
  - admin_required: blocks a command unless the active user is an Admin
  - log_action("description"): writes an entry to data/activity_log.json
    every time a decorated command runs (simple audit trail)

Each decorated function is expected to receive a `session` object
(see session.Session) as its first argument.
"""

import functools
from datetime import datetime

from utils import storage


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
    """Ensure the logged-in user is an Admin before running func."""
    @functools.wraps(func)
    def wrapper(session, *args, **kwargs):
        if session.current_user is None:
            print("You must be logged in to do that.")
            return None
        if not session.current_user.can_manage_users():
            print("Permission denied: this action requires an admin role.")
            return None
        return func(session, *args, **kwargs)
    return wrapper


def log_action(description: str):
    """Decorator factory: append a timestamped audit entry every time the decorated command runs."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(session, *args, **kwargs):
            result = func(session, *args, **kwargs)
            username = session.current_user.username if session.current_user else "anonymous"
            storage.append_log({
                "timestamp": datetime.now().isoformat(),
                "username": username,
                "action": description,
            })
            return result
        return wrapper
    return decorator
