"""
auth.py
Session class: ties together the UserRepository with a lightweight
"who is currently logged in" concept.

Because each argparse invocation is a fresh process, the logged-in
username is persisted to data/session.json between commands (not the
password/hash - just a pointer to who is logged in). Interactive mode
uses the same Session object in-memory for the life of the menu loop.
"""

import os
from utils.repository import UserRepository
from utils.storage import load_json, save_json, DATA_DIR

SESSION_FILE = "session.json"


class Session:
    def __init__(self):
        self.users = UserRepository()
        self.current_user = self._load_session_user()

    def _load_session_user(self):
        records = load_json(SESSION_FILE)
        if records and isinstance(records, list) and records:
            username = records[0].get("username")
            return self.users.find_by_username(username) if username else None
        return None

    def _persist_session(self):
        if self.current_user:
            save_json(SESSION_FILE, [{"username": self.current_user.username}])
        else:
            save_json(SESSION_FILE, [])

    def register(self, username: str, name: str, email: str, password: str, role: str = "user"):
        from models.user import User
        if self.users.exists(username):
            raise ValueError(f"Username {username!r} is already taken.")
        user = User(username=username, name=name, email=email, role=role, password=password)
        self.users.add(user)
        return user

    def login(self, username: str, password: str) -> bool:
        user = self.users.find_by_username(username)
        if user is None or not user.verify_password(password):
            return False
        self.current_user = user
        self._persist_session()
        return True

    def logout(self):
        self.current_user = None
        self._persist_session()
