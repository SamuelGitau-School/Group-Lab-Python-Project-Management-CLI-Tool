"""
session.py

Session ties an AuthManager (registration/login business rules) to
the concept of "who is currently logged in right now". Because each
one-shot `python main.py ...` invocation is a fresh process, the
logged-in username is persisted to data/session.json between
commands (never the password/hash - just a pointer to who is logged
in). Interactive mode just keeps one Session object alive for the
life of the menu loop, so the file round-trip only matters for
one-shot mode.
"""

from auth.auth_manager import AuthManager
from utils import storage


class Session:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.current_user = self._load_current_user()

    def _load_current_user(self):
        username = storage.load_session()
        if not username:
            return None
        return self.auth_manager.users.find_by_username(username)

    def login(self, username: str, password: str) -> bool:
        user = self.auth_manager.login(username, password)
        if user is None:
            return False
        self.current_user = user
        storage.save_session(user.username)
        return True

    def logout(self) -> None:
        self.current_user = None
        storage.clear_session()
