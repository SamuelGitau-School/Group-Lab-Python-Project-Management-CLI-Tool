"""
utils/repository.py

UserRepository: the repository pattern TaskFlow's auth.py builds on
(a UserRepository sitting between Session/AuthManager and raw
storage). Chess_cli already had a working utils.storage with plain
load_users()/save_users() dict functions, so this wraps those behind
an object with domain-shaped methods (find_by_username, exists, add)
instead of duplicating TaskFlow's own storage layer.

AuthManager talks to this, never to utils.storage directly - one
more layer of separation between "business rules for accounts" and
"how accounts are written to disk".
"""

from models.user import User
from utils.storage import load_users, save_users


class UserRepository:
    def __init__(self):
        self._users = load_users()  # dict[username] -> user dict

    def exists(self, username: str) -> bool:
        return self._key(username) in self._users

    def find_by_username(self, username: str):
        data = self._users.get(self._key(username))
        return User.from_dict(data) if data else None

    @staticmethod
    def _key(username: str) -> str:
        # User.username always stores lowercase/stripped, so lookups
        # must normalize the same way
        # (e.g. registering "Grace" after "GRACE") would slip past
        # exists() and silently overwrite instead of being rejected.
        return (username or "").strip().lower()

    def add(self, user) -> None:
        self._users[user.username] = user.to_dict()
        save_users(self._users)

    def all_usernames(self) -> list:
        return list(self._users.keys())
