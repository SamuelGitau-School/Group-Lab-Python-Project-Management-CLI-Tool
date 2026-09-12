"""
auth/auth_manager.py

AuthManager owns registration and login logic. It talks to
utils.repository.UserRepository (not raw file I/O) for persistence
and to models.user for the User/Admin objects. Kept separate from
the CLI so auth logic is testable and reusable - and kept separate
from storage so the repository could be swapped out without
touching a single line of register()/login().
"""

from typing import Optional

from models.user import User, Admin
from utils.repository import UserRepository


class AuthManager:
    def __init__(self):
        self.users = UserRepository()

    # BUG (fixed): was
    #     def register(self, username: str, password: str, role: str = "user",
    #                  name: str = None, email: str = None) -> tuple:
    # Same str/None contradiction as hash_password() and User.__init__ -
    # name/email are optional (see docstring in models/user.py), so the
    # type hint should say Optional[str], not str.
    def register(self, username: str, password: str, role: str = "user",
                 name: Optional[str] = None, email: Optional[str] = None) -> tuple:
        username = username.strip()
        if not username or not password:
            return False, "Username and password cannot be empty."
        if self.users.exists(username):
            return False, f"Username '{username}' already exists."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        # BUG (fixed): there used to be no role check here at all. The
        # argparse entry point (main.py) restricts role via
        # choices=["user","admin"], but the interactive REPL (cli.py)
        # passes through whatever word the user typed unchecked - so
        # e.g. `register bob pass1234 superadmin` reached this point
        # with role="superadmin".
        if role not in ("user", "admin"):
            return False, f"Invalid role {role!r}; must be 'user' or 'admin'."

        cls = Admin if role == "admin" else User
        try:
            user = cls(username=username, raw_password=password, name=name, email=email)
        except ValueError as exc:
            # Person/User property setters (e.g. username too short,
            # malformed email) raise here instead of writing bad data.
            return False, str(exc)

        self.users.add(user)
        # BUG (fixed): this used to be
        #     return True, f"User '{username}' registered as {role}."
        # which echoed the raw, unvalidated `role` argument. Because
        # `cls` above only becomes Admin when role == "admin" exactly,
        # an invalid role like "superadmin" silently created a plain
        # User while the message still claimed "registered as
        # superadmin". Now it reports the account's actual role.
        return True, f"User '{username}' registered as {user.role}."

    def login(self, username: str, password: str):
        """Returns a User/Admin instance on success, or None on failure."""
        user = self.users.find_by_username(username.strip())
        if user is None or not user.check_password(password):
            return None
        return user

    def list_usernames(self) -> list:
        return self.users.all_usernames()