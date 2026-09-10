"""
models/user.py

User model demonstrating inheritance across two levels:
Person -> User -> Admin. Person (ported from TaskFlow) owns the
name/email fields; User adds authentication + role and its own
validated `username` property (same pattern TaskFlow uses on its
User class); Admin overrides exactly one method. The password hash
is stored as a protected attribute and never exposed directly
(encapsulation) - only check_password() may look at it.

name/email are optional at the call sites that create a User
(register only ever asked for username/password/role) so they
default to values derived from the username - the fields exist and
are validated the same way TaskFlow's are, without forcing every
existing `register <username> <password>` call to change.
"""

from models.person import Person
from utils.security import hash_password, verify_password


class User(Person):
    role = "user"

    # Class attribute shared by every instance: a simple in-memory
    # ID counter (per process run) so each User object created has a
    # unique numeric id, separate from its username.
    _id_counter = 0

    def __init__(self, username: str, password_hash: str = None, raw_password: str = None,
                 name: str = None, email: str = None):
        display_name = name or username
        contact_email = email or f"{username}@chess.local"
        super().__init__(display_name, contact_email)

        User._id_counter += 1
        self._id = User._id_counter

        self._username = None
        self.username = username

        if raw_password is not None:
            self._password_hash = hash_password(raw_password)
        else:
            self._password_hash = password_hash

    # Encapsulated attribute (ported pattern from TaskFlow's User.username)
    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or len(value.strip()) < 3:
            raise ValueError("Username must be at least 3 characters.")
        self._username = value.strip().lower()

    @property
    def user_id(self) -> int:
        return self._id

    def check_password(self, raw_password: str) -> bool:
        return verify_password(raw_password, self._password_hash)

    def can_manage_users(self) -> bool:
        """Base users cannot manage other accounts."""
        return False

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password_hash": self._password_hash,
            "role": self.role,
            "name": self.name,
            "email": self.email,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id}, username={self.username!r}, role={self.role!r})"

    @staticmethod
    def from_dict(data: dict) -> "User":
        role = data.get("role", "user")
        cls = Admin if role == "admin" else User
        return cls(
            username=data["username"],
            password_hash=data["password_hash"],
            name=data.get("name"),
            email=data.get("email"),
        )


class Admin(User):
    """Admin inherits from User and overrides permission behavior."""

    role = "admin"

    def can_manage_users(self) -> bool:
        return True
