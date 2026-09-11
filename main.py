#!/usr/bin/env python3
"""
Usage:
    python main.py                            -> interactive REPL mode
    python main.py register alice secret123 [role]
    python main.py login alice secret123
    python main.py logout
    python main.py show-moves --piece bishop --square e4 [--username alice --password secret123]
    python main.py log [--username bossman --password adminpass]

show-moves/log reuse the persisted session (data/session.json) from a
prior `login` invocation when --username/--password are omitted, so
you can log in once and run several one-shot commands afterward.
"""

import argparse
import sys

from tabulate import tabulate

import commands as c
import cli
from session import Session


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chess_cli", description="Chess Move Showcase CLI")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("register", help="Create a new account")
    p.add_argument("username")
    p.add_argument("password")
    p.add_argument("role", nargs="?", default="user", choices=["user", "admin"])

    p = sub.add_parser("login", help="Log in and persist the session")
    p.add_argument("username")
    p.add_argument("password")

    sub.add_parser("logout", help="Log out of the current session")

    p = sub.add_parser("show-moves", help="Show every legal destination square for a piece")
    p.add_argument("--piece", required=True, help="bishop, knight, or queen")
    p.add_argument("--square", required=True, help="e.g. d4")
    p.add_argument("--username")
    p.add_argument("--password")

    p = sub.add_parser("log", help="Show the activity log (admin only)")
    p.add_argument("--username")
    p.add_argument("--password")

    return parser


def _maybe_login(session: Session, args) -> None:
    if getattr(args, "username", None) and getattr(args, "password", None):
        session.login(args.username, args.password)


def dispatch(args, session: Session) -> None:
    if args.command == "register":
        ok, message = c.cmd_register(session, args.username, args.password, role=args.role)
        print(message)

    elif args.command == "login":
        if c.cmd_login(session, args.username, args.password):
            print(f"Welcome back, {session.current_user.username}.")
        else:
            print("Invalid username or password.")

    elif args.command == "logout":
        was_logged_in = session.current_user is not None
        c.cmd_logout(session)
        print("Logged out." if was_logged_in else "You were not logged in.")

    elif args.command == "show-moves":
        _maybe_login(session, args)
        result = c.cmd_show_moves(session, args.piece, args.square)
        if result is None:
            return
        piece, moves = result
        print(c.render_moves_board(piece, moves))
        if moves:
            rows = [(c.square_name(row, col),) for row, col in moves]
            print(tabulate(rows, headers=["Destination"]))
        else:
            print("No legal moves from this square.")

    elif args.command == "log":
        _maybe_login(session, args)
        entries = c.cmd_log(session)
        if entries is None:
            return
        if not entries:
            print("No activity logged yet.")
            return
        rows = [(e["at"], e["who"], e["action"]) for e in entries]
        print(tabulate(rows, headers=["When", "Who", "Action"]))


def main():
    parser = build_parser()
    args = parser.parse_args()
    session = Session()

    if args.command is None:
        # No subcommand given -> drop into interactive REPL mode
        cli.run(session)
        return

    try:
        dispatch(args, session)
    except ValueError as exc:
        print(f"[error] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
