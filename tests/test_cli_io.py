"""
tests/test_cli_io.py

Mocked-input tests for cli.py's interactive REPL: feeds a scripted
sequence of `chess>` command lines through builtins.input and asserts
on what gets printed, so register -> login -> show-moves -> log is
exercised the way a real user would type it, without a real terminal
and without ever touching real data/*.json.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import importlib
import pytest


@pytest.fixture
def isolated_session(tmp_path, monkeypatch):
    import utils.storage as storage
    monkeypatch.setattr(storage, "DATA_DIR", str(tmp_path))
    monkeypatch.setattr(storage, "USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr(storage, "LOG_FILE", str(tmp_path / "activity_log.json"))

    import session as session_module
    importlib.reload(session_module)
    import commands as commands_module
    importlib.reload(commands_module)
    import cli as cli_module
    importlib.reload(cli_module)

    return session_module.Session(), cli_module


def _run_repl(cli_module, session, lines, monkeypatch):
    responses = iter(lines)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(responses))
    cli_module.run(session)


def test_register_login_and_show_moves(isolated_session, monkeypatch, capsys):
    session, cli_module = isolated_session
    lines = [
        "register alice secret123",
        "login alice secret123",
        "show-moves knight d4",
        "quit",
    ]
    _run_repl(cli_module, session, lines, monkeypatch)
    out = capsys.readouterr().out

    assert "registered as user" in out
    assert "Welcome back, alice." in out
    assert "Destination" in out
    # A knight on d4 has exactly these 8 legal destinations.
    for square in ("c2", "e2", "c6", "e6", "b3", "f3", "b5", "f5"):
        assert square in out


def test_unknown_command_does_not_crash(isolated_session, monkeypatch, capsys):
    session, cli_module = isolated_session
    _run_repl(cli_module, session, ["dance", "quit"], monkeypatch)
    out = capsys.readouterr().out
    assert "Unknown command 'dance'" in out


def test_show_moves_rejects_unknown_piece(isolated_session, monkeypatch, capsys):
    session, cli_module = isolated_session
    lines = [
        "register alice secret123",
        "login alice secret123",
        "show-moves rook d4",
        "quit",
    ]
    _run_repl(cli_module, session, lines, monkeypatch)
    out = capsys.readouterr().out
    assert "Unknown piece 'rook'" in out


def test_show_moves_rejects_bad_square(isolated_session, monkeypatch, capsys):
    session, cli_module = isolated_session
    lines = [
        "register alice secret123",
        "login alice secret123",
        "show-moves bishop z9",
        "quit",
    ]
    _run_repl(cli_module, session, lines, monkeypatch)
    out = capsys.readouterr().out
    assert "[error] Invalid square" in out


def test_show_moves_requires_login(isolated_session, monkeypatch, capsys):
    session, cli_module = isolated_session
    _run_repl(cli_module, session, ["show-moves knight d4", "quit"], monkeypatch)
    out = capsys.readouterr().out
    assert "must be logged in" in out


def test_non_admin_cannot_view_log(isolated_session, monkeypatch, capsys):
    session, cli_module = isolated_session
    lines = [
        "register dave secret123",
        "login dave secret123",
        "log",
        "quit",
    ]
    _run_repl(cli_module, session, lines, monkeypatch)
    out = capsys.readouterr().out
    assert "Permission denied" in out


def test_admin_can_view_log_after_activity(isolated_session, monkeypatch, capsys):
    session, cli_module = isolated_session
    lines = [
        "register boss adminpass admin",
        "login boss adminpass",
        "show-moves queen a1",
        "log",
        "quit",
    ]
    _run_repl(cli_module, session, lines, monkeypatch)
    out = capsys.readouterr().out
    assert "When" in out and "Who" in out and "Action" in out
    assert "boss" in out
    assert "logged in" in out
