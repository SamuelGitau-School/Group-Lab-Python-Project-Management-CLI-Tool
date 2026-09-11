"""
session.py

Session: the "who is currently logged in" wrapper that survives
between separate `python main.py ...` invocations. Each invocation is
a fresh process, so the logged-in username - never a password or
token - is persisted to data/session.json. AuthManager (and the
UserRepository underneath it) still owns every actual auth rule;
Session only adds that cross-process pointer.
"""

from auth.auth_manager import AuthManager
from utils.storage import load_json, save_json

SESSION_FILE = "session.json"


class Session:
    def __init__(self):
        self.auth_manager = AuthManager()
        self.current_user = self._load_current_user()

    def _load_current_user(self):
        records = load_json(SESSION_FILE)
        if records:
            username = records[0].get("username")
            return self.auth_manager.users.find_by_username(username) if username else None
        return None

    def _persist(self) -> None:
        if self.current_user:
            save_json(SESSION_FILE, [{"username": self.current_user.username}])
        else:
            save_json(SESSION_FILE, [])

    def register(self, username, password, role="user", name=None, email=None):
        """Returns (ok: bool, message: str) - passed straight through from AuthManager."""
        return self.auth_manager.register(username, password, role=role, name=name, email=email)

    def login(self, username, password) -> bool:
        user = self.auth_manager.login(username, password)
        if user is None:
            return False
        self.current_user = user
        self._persist()
        return True

    def logout(self) -> None:
        self.current_user = None
        self._persist()
