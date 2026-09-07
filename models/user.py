"""
user.py
Defines the User class (inherits Person). Handles secure password
hashing (PBKDF2 + per-user salt, stdlib only, no plaintext ever stored)
and role-based access (admin/user).
"""

from __future__ import annotations
import hashlib
import os
import binascii
from datetime import datetime, timezone

from .person import Person

VALID_ROLES = ("admin", "user")


class User(Person):
    """
    Represents a system account. Inherits name/email handling from Person
    and adds authentication + role-based access concerns.
    """

    _id_counter = 1  # class attribute: auto-incrementing id generator

    def __init__(self, username: str, name: str, email: str, role: str = "user",
                 user_id: int = None, password: str = None,
                 password_hash: str = None, salt: str = None,
                 created_at: str = None):
        super().__init__(name, email)

        self._username = None
        self._role = None
        self.username = username
        self.role = role

        if user_id is not None:
            self.user_id = user_id
            # keep the class counter ahead of any loaded id
            User._id_counter = max(User._id_counter, user_id + 1)
        else:
            self.user_id = User._id_counter
            User._id_counter += 1

        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

        if password_hash and salt:
            # Reconstructing from storage
            self._salt = salt
            self._password_hash = password_hash
        elif password:
            # Fresh registration
            self._salt = binascii.hexlify(os.urandom(16)).decode()
            self._password_hash = self._hash_password(password, self._salt)
        else:
            raise ValueError("Either a plaintext password or a stored hash+salt is required.")

    # ---------- Encapsulation ----------
    @property
    def username(self) -> str:
        return self._username

    @username.setter
    def username(self, value: str):
        if not value or len(value.strip()) < 3:
            raise ValueError("Username must be at least 3 characters.")
        self._username = value.strip().lower()

    @property
    def role(self) -> str:
        return self._role

    @role.setter
    def role(self, value: str):
        value = str(value).strip().lower()
        if value not in VALID_ROLES:
            raise ValueError(f"Role must be one of {VALID_ROLES}, got {value!r}")
        self._role = value

    @property
    def is_admin(self) -> bool:
        return self._role == "admin"

    # ---------- Password handling (private-ish, name-mangled helpers) ----------
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
        )
        return binascii.hexlify(dk).decode()

    def verify_password(self, password: str) -> bool:
        """Check a plaintext password attempt against the stored hash."""
        attempt_hash = self._hash_password(password, self._salt)
        return attempt_hash == self._password_hash

    def change_password(self, new_password: str) -> None:
        self._salt = binascii.hexlify(os.urandom(16)).decode()
        self._password_hash = self._hash_password(new_password, self._salt)

    # ---------- Serialization ----------
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "password_hash": self._password_hash,
            "salt": self._salt,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            username=data["username"],
            name=data["name"],
            email=data["email"],
            role=data.get("role", "user"),
            user_id=data.get("user_id"),
            password_hash=data.get("password_hash"),
            salt=data.get("salt"),
            created_at=data.get("created_at"),
        )

    def __str__(self) -> str:
        return f"[{self.user_id}] {self.username} ({self.role}) - {self.name} <{self.email}>"

    def __repr__(self) -> str:
        return f"User(username={self.username!r}, role={self.role!r})"
