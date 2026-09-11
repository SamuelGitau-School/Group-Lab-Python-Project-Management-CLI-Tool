"""
cli.py

Interactive REPL front end: a `chess>` prompt that reads a command
word plus arguments (like a tiny shell), not a numbered menu - matches
README's `chess> show-moves knight d4` style. Every command dispatches
to the same commands.py handlers main.py's argparse subcommands use,
so both entry points share one set of business rules; this file only
owns parsing the line, printing usage on a bad call, and rendering
results (tabulate tables for the move list and the activity log).

Every dispatched command runs inside one try/except in the loop
itself, so a bad argument (an invalid square, an unknown piece) is
reported and the prompt keeps going instead of crashing.
"""

from tabulate import tabulate

import commands as c


def _cmd_register(session, args):
    if len(args) not in (2, 3):
        print("Usage: register <username> <password> [role]")
        return
    username, password = args[0], args[1]
    role = args[2] if len(args) == 3 else "user"
    ok, message = c.cmd_register(session, username, password, role=role)
    print(message)


def _cmd_login(session, args):
    if len(args) != 2:
        print("Usage: login <username> <password>")
        return
    if c.cmd_login(session, args[0], args[1]):
        print(f"Welcome back, {session.current_user.username}.")
    else:
        print("Invalid username or password.")


def _cmd_logout(session, args):
    name = session.current_user.username if session.current_user else None
    c.cmd_logout(session)
    print(f"Goodbye, {name}." if name else "You were not logged in.")


def _cmd_show_moves(session, args):
    if len(args) != 2:
        print("Usage: show-moves <piece> <square>")
        return
    result = c.cmd_show_moves(session, args[0], args[1])
    if result is None:
        return
    piece, moves = result
    print(c.render_moves_board(piece, moves))
    if moves:
        rows = [(c.square_name(row, col),) for row, col in moves]
        print(tabulate(rows, headers=["Destination"]))
    else:
        print("No legal moves from this square.")


def _cmd_log(session, args):
    entries = c.cmd_log(session)
    if entries is None:
        return
    if not entries:
        print("No activity logged yet.")
        return
    rows = [(e["at"], e["who"], e["action"]) for e in entries]
    print(tabulate(rows, headers=["When", "Who", "Action"]))


def _cmd_help(session, args):
    print(
        "Commands:\n"
        "  register <username> <password> [role]\n"
        "  login <username> <password>\n"
        "  logout\n"
        "  show-moves <bishop|knight|queen> <square>   e.g. show-moves knight d4\n"
        "  log                                          (admin only)\n"
        "  quit"
    )


_COMMANDS = {
    "register": _cmd_register,
    "login": _cmd_login,
    "logout": _cmd_logout,
    "show-moves": _cmd_show_moves,
    "log": _cmd_log,
    "help": _cmd_help,
}


def run(session) -> None:
    print("Welcome to the Chess Move Showcase CLI. Type 'help' for commands, 'quit' to exit.")
    while True:
        try:
            line = input("chess> ").strip()
        except EOFError:
            print()
            return

        if not line:
            continue

        word, *args = line.split()
        word = word.lower()

        if word in ("quit", "exit"):
            print("Goodbye.")
            return

        handler = _COMMANDS.get(word)
        if handler is None:
            print(f"Unknown command {word!r}. Type 'help' for the list of commands.")
            continue

        try:
            handler(session, args)
        except ValueError as exc:
            print(f"[error] {exc}")
