"""
utils/security.py

Password hashing helpers, built on Python's standard library
(hashlib + a per-password random salt via secrets). No plaintext
passwords are ever stored.
"""

import hashlib
import secrets
from typing import Optional


# BUG (fixed): was `def hash_password(raw_password: str, salt: str = None) -> str:`
# The type hint said `salt` is always a `str`, but the default value is
# `None` - a contradiction a type checker (Pylance/Pyright) flags as
# "Expression of type None cannot be assigned to parameter of type str".
# It ran fine at runtime (Python doesn't enforce type hints), but the
# annotation was simply wrong. `Optional[str]` documents that None is a
# valid input, matching the `if salt is None:` check right below it.
def hash_password(raw_password: str, salt: Optional[str] = None) -> str:
    """
    Returns a string in the form 'salt$hash' using PBKDF2-HMAC-SHA256.
    A fresh random salt is generated unless one is supplied (used
    internally when verifying).
    """
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        raw_password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${digest}"


# BUG (fixed): was `def verify_password(raw_password: str, stored_hash: str) -> bool:`
# User._password_hash (models/user.py) is Optional[str] - it's None if a
# User is ever constructed with neither raw_password nor password_hash.
# check_password() passes that value straight through here, so this
# parameter can genuinely be None.
#
# Just widening the annotation to Optional[str] isn't enough on its
# own: the old body relied on `stored_hash.split(...)` raising
# AttributeError on None and catching that below, which works at
# runtime but a type checker can't see through a try/except as
# narrowing - it would keep flagging the .split() call itself. An
# explicit `if stored_hash is None: return False` narrows the type
# properly, so it's clearer for a human reader too.
def verify_password(raw_password: str, stored_hash: Optional[str]) -> bool:
    if stored_hash is None:
        return False
    try:
        salt, _ = stored_hash.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(hash_password(raw_password, salt), stored_hash)