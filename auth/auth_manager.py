"""
auth/auth_manager.py

AuthManager owns registration and login logic. It talks to
utils.repository.UserRepository (not raw file I/O) for persistence
and to models.user for the User/Admin objects. Kept separate from
the CLI so auth logic is testable and reusable - and kept separate
from storage so the repository could be swapped out without
touching a single line of register()/login().
"""

from models.user import User, Admin
from utils.repository import UserRepository


class AuthManager:
    def __init__(self):
        self.users = UserRepository()

    def register(self, username: str, password: str, role: str = "user",
                 name: str = None, email: str = None) -> tuple:
        username = username.strip()
        if not username or not password:
            return False, "Username and password cannot be empty."
        if self.users.exists(username):
            return False, f"Username '{username}' already exists."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."

        cls = Admin if role == "admin" else User
        try:
            user = cls(username=username, raw_password=password, name=name, email=email)
        except ValueError as exc:
            # Person/User property setters (e.g. username too short,
            # malformed email) raise here instead of writing bad data.
            return False, str(exc)

        self.users.add(user)
        return True, f"User '{username}' registered as {role}."

    def login(self, username: str, password: str):
        """Returns a User/Admin instance on success, or None on failure."""
        user = self.users.find_by_username(username.strip())
        if user is None or not user.check_password(password):
            return None
        return user

    def list_usernames(self) -> list:
        return self.users.all_usernames()
