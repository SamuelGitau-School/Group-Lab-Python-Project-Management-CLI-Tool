"""
utils/security.py

Password hashing helpers, built on Python's standard library
(hashlib + a per-password random salt via secrets). No plaintext
passwords are ever stored.
"""

import hashlib
import secrets


def hash_password(raw_password: str, salt: str = None) -> str:
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


def verify_password(raw_password: str, stored_hash: str) -> bool:
    try:
        salt, _ = stored_hash.split("$", 1)
    except (ValueError, AttributeError):
        return False
    return secrets.compare_digest(hash_password(raw_password, salt), stored_hash)
