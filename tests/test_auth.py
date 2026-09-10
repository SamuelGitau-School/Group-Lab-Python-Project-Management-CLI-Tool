"""
tests/test_auth.py

Tests for registration/login logic. Uses a temporary data directory
so tests never touch the real data/users.json file.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib
import pytest


@pytest.fixture
def auth_manager(tmp_path, monkeypatch):
    # Redirect storage paths to a temp directory for test isolation
    import utils.storage as storage
    monkeypatch.setattr(storage, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(storage, "USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(storage, "LOG_FILE", str(tmp_path / "activity_log.json"))

    import auth.auth_manager as auth_manager_module
    importlib.reload(auth_manager_module)
    return auth_manager_module.AuthManager()


def test_register_new_user_succeeds(auth_manager):
    ok, message = auth_manager.register("alice", "secret123")
    assert ok is True
    assert "alice" in auth_manager.list_usernames()


def test_register_duplicate_user_fails(auth_manager):
    auth_manager.register("alice", "secret123")
    ok, message = auth_manager.register("alice", "otherpass")
    assert ok is False
    assert "already exists" in message


def test_register_short_password_fails(auth_manager):
    ok, message = auth_manager.register("bob", "abc")
    assert ok is False


def test_login_correct_credentials(auth_manager):
    auth_manager.register("alice", "secret123")
    user = auth_manager.login("alice", "secret123")
    assert user is not None
    assert user.username == "alice"


def test_login_wrong_password_fails(auth_manager):
    auth_manager.register("alice", "secret123")
    user = auth_manager.login("alice", "wrongpass")
    assert user is None


def test_login_unknown_user_fails(auth_manager):
    user = auth_manager.login("ghost", "whatever")
    assert user is None


def test_admin_role_permissions(auth_manager):
    auth_manager.register("boss", "adminpass", role="admin")
    user = auth_manager.login("boss", "adminpass")
    assert user.can_manage_users() is True


def test_register_defaults_name_and_email(auth_manager):
    """Person fields are optional at register() but always get set."""
    auth_manager.register("dave", "secret123")
    user = auth_manager.login("dave", "secret123")
    assert user.name == "dave"
    assert user.email == "dave@chess.local"


def test_register_custom_name_and_email(auth_manager):
    auth_manager.register("erin", "secret123", name="Erin Reyes", email="Erin@Example.com")
    user = auth_manager.login("erin", "secret123")
    assert user.name == "Erin Reyes"
    assert user.email == "erin@example.com"  # Person lowercases stored email


def test_register_too_short_username_fails(auth_manager):
    ok, message = auth_manager.register("ab", "secret123")
    assert ok is False
    assert "at least 3 characters" in message


def test_register_invalid_email_fails(auth_manager):
    ok, message = auth_manager.register("frank", "secret123", email="not-an-email")
    assert ok is False
    assert "Invalid email" in message


def test_username_stored_lowercase(auth_manager):
    auth_manager.register("GRACE", "secret123")
    assert "grace" in auth_manager.list_usernames()
    assert auth_manager.login("grace", "secret123") is not None


@pytest.mark.parametrize("bad_email", ["", "no-at-sign", "user@nodot"])
def test_person_rejects_bad_email_directly(bad_email):
    from models.person import Person
    with pytest.raises(ValueError):
        Person("Someone", bad_email)


def test_session_persists_login_across_separate_process(tmp_path, monkeypatch):
    """
    Simulates two separate `python main.py ...` invocations: a fresh
    Session() in the second one should already be logged in, because
    `login` on the first Session() persisted the username to
    data/session.json (ported from TaskFlow's Session).
    """
    import utils.storage as storage
    monkeypatch.setattr(storage, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(storage, "USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(storage, "LOG_FILE", str(tmp_path / "activity_log.json"))

    import importlib
    import session as session_module
    importlib.reload(session_module)

    first = session_module.Session()
    first.auth_manager.register("hank", "secret123")
    first.login("hank", "secret123")

    # Brand-new Session object = a brand-new process would have done this
    second = session_module.Session()
    assert second.current_user is not None
    assert second.current_user.username == "hank"

    second.logout()
    third = session_module.Session()
    assert third.current_user is None
