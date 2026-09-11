"""
commands.py

Command handlers shared by the argparse subcommands (main.py) and the
interactive REPL (cli.py): register/login/logout, show-moves (every
legal destination square for a Bishop/Knight/Queen on an otherwise
empty board), and log (admin-only activity audit trail).

@login_required / @admin_required / @validate_piece_name /
@log_action(...) (utils/decorators.py) do all the cross-cutting work,
so these functions stay pure business logic: pull data from
session/models, return it, and raise ValueError for anything the
caller needs to report (a malformed square). Neither entry point
prints in here - main.py and cli.py render the results (main.py plain
text, cli.py/main.py both use tabulate for the move list and the log)
from the same return values.
"""

from models.board import Board
from models.pieces import Bishop, Knight, Queen
from utils.decorators import login_required, admin_required, log_action, validate_piece_name
from utils.storage import load_log, log_activity

PIECE_CLASSES = {"bishop": Bishop, "knight": Knight, "queen": Queen}


# ---------------------------------------------------------------- auth

@log_action("registered a new account")
def cmd_register(session, username, password, role="user"):
    return session.register(username, password, role=role)


@log_action("logged in")
def cmd_login(session, username, password):
    return session.login(username, password)


def cmd_logout(session):
    # Not @log_action: that decorator reads session.current_user *after*
    # the call, but logout's whole job is to clear it - logging here
    # directly, before the clear, is what actually attributes the entry.
    who = session.current_user.username if session.current_user else "anonymous"
    session.logout()
    log_activity(who, "logged out")


# ------------------------------------------------------------ show-moves

def _parse_square(square: str):
    normalized = (square or "").strip().lower()
    if len(normalized) != 2 or normalized[0] not in "abcdefgh" or normalized[1] not in "12345678":
        raise ValueError(f"Invalid square {square!r}; expected a file a-h and a rank 1-8, e.g. 'd4'.")
    col = ord(normalized[0]) - ord("a")
    row = int(normalized[1]) - 1
    return row, col


def square_name(row: int, col: int) -> str:
    return f"{chr(ord('a') + col)}{row + 1}"


@login_required
@validate_piece_name
@log_action("looked up piece moves")
def cmd_show_moves(session, piece_name, square):
    row, col = _parse_square(square)
    piece = PIECE_CLASSES[piece_name](color="white", row=row, col=col)
    board = Board()
    board.place(piece)
    moves = piece.get_legal_moves(board)
    return piece, moves


def render_moves_board(piece, moves) -> str:
    """ASCII board: the piece's letter on its square, 'x' on every
    legal destination, '.' everywhere else - otherwise empty board."""
    move_set = set(moves)
    lines = []
    for row in range(7, -1, -1):
        cells = []
        for col in range(8):
            if (row, col) == piece.position:
                symbol = piece.symbol if piece.color == "white" else piece.symbol.lower()
                cells.append(symbol)
            elif (row, col) in move_set:
                cells.append("x")
            else:
                cells.append(".")
        lines.append(f"{row + 1} " + " ".join(cells))
    lines.append("  " + " ".join("abcdefgh"))
    return "\n".join(lines)


# --------------------------------------------------------------- activity log

@admin_required
def cmd_log(session):
    return load_log()
