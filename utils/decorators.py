"""
utils/decorators.py

Guards for the command handlers in commands.py:
  - login_required: blocks an action unless a Session has a user.
  - admin_required: blocks an action unless the current user can
    manage users - checked via User.can_manage_users() rather than a
    role string, so it stays correct if another User subclass besides
    Admin ever overrides that method.
  - validate_piece_name: rejects anything but bishop/knight/queen
    before a show-moves call ever touches the board/piece models.
  - log_action(description): a decorator *factory* - wrap a handler
    with @log_action("did the thing") and every successful call
    appends {who, action, at} to the audit trail (utils.storage).

Each decorated function receives `session` as its first argument.
"""

import functools

from utils.storage import log_activity

PIECE_NAMES = ("bishop", "knight", "queen")


def login_required(func):
    @functools.wraps(func)
    def wrapper(session, *args, **kwargs):
        if session.current_user is None:
            print("You must be logged in to do that. Try `login` first.")
            return None
        return func(session, *args, **kwargs)
    return wrapper


def admin_required(func):
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


def validate_piece_name(func):
    @functools.wraps(func)
    def wrapper(session, piece_name, *args, **kwargs):
        normalized = (piece_name or "").strip().lower()
        if normalized not in PIECE_NAMES:
            print(f"Unknown piece {piece_name!r}. Choose one of: {', '.join(PIECE_NAMES)}.")
            return None
        return func(session, normalized, *args, **kwargs)
    return wrapper


def log_action(description: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(session, *args, **kwargs):
            result = func(session, *args, **kwargs)
            who = session.current_user.username if session.current_user else "anonymous"
            log_activity(who, description)
            return result
        return wrapper
    return decorator
