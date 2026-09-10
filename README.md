# Chess Move Showcase CLI

An interactive, object-oriented command-line tool that shows every
legal-shape destination square for the **Bishop**, **Knight**, and
**Queen** on an empty chessboard — with a real login system and
persistent JSON storage.

## Features

- **Object-oriented design**: an abstract `Piece` base class with
  `Bishop`, `Knight`, and `Queen` subclasses (inheritance +
  polymorphism); a `User` / `Admin` hierarchy for role-based access
  (encapsulation of the password hash).
- **Authentication**: registration, login, PBKDF2 password hashing
  (no plaintext passwords stored, ever), and Admin vs. User roles.
- **Persistence**: users and an activity log are stored in JSON
  files under `data/`.
- **Decorators**: `@login_required`, `@admin_required`,
  `@log_action("...")`, and `@validate_piece_name` wrap the command
  functions to keep cross-cutting concerns out of the business logic.
- **Two CLI modes**:
  - **Interactive** menu-driven REPL (`python main.py`)
  - **One-shot** `argparse` subcommands (`python main.py show-moves --piece knight --square d4 --username alice --password secret123`)
- **ASCII board rendering** that highlights the piece (its letter)
  and every possible destination (`x`).
- **External package**: uses [`tabulate`](https://pypi.org/project/tabulate/)
  to render the move list and admin activity log as clean tables.
- **Class attributes**: `Piece` and `User` each keep a class-level
  `_id_counter` so every instance gets a unique numeric ID.
- **Property setters**: `Piece.color` and `Piece.position` are real
  properties with setters that validate input before writing to the
  underlying `_color`/`_position` attributes.
- **Unit tests** with `pytest`, including mocked input/output tests
  for the interactive REPL (`tests/test_cli_io.py`).

## Project structure

```
chess_cli/
├── main.py                # Entry point (argparse + interactive fallback)
├── cli.py                 # Interactive REPL menu loop
├── session.py              # Session state (current logged-in user)
├── commands.py             # Command functions (decorated business logic)
├── models/
│   ├── piece.py            # Piece, Bishop, Knight, Queen
│   ├── board.py             # ASCII board rendering
│   └── user.py               # User / Admin
├── auth/
│   └── auth_manager.py       # Register / login logic
├── utils/
│   ├── security.py             # Password hashing (PBKDF2 + salt)
│   ├── storage.py                # JSON persistence
│   └── decorators.py               # login_required, admin_required, log_action, validate_piece_name
├── data/
│   ├── users.json                    # Created on first registration
│   └── activity_log.json               # Created on first logged action
├── tests/
│   ├── test_pieces.py                    # Move-generation unit tests
│   └── test_auth.py                        # Registration/login unit tests
├── requirements.txt
└── README.md
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Interactive mode (recommended)

```bash
python main.py
```

```
chess> register alice secret123
chess> login alice secret123
chess> show-moves knight d4
chess> log            # only works if logged in as an admin
chess> quit
```

To create an admin account: `register bossman adminpass admin`

### One-shot mode

```bash
python main.py register alice secret123
python main.py show-moves --piece bishop --square e4 --username alice --password secret123
python main.py log --username bossman --password adminpass
```

## Running tests

```bash
pytest
```

## Design notes

- Move generation assumes an **otherwise empty board** — the focus
  of this tool is showing each piece's *movement pattern*, not
  simulating a full game with captures/checks.
- Passwords are hashed with PBKDF2-HMAC-SHA256 and a random 16-byte
  salt per user; the raw password is never written to disk.
- `commands.py` intentionally contains no auth/logging code itself —
  that's all handled by the decorators in `utils/decorators.py`,
  which keeps the business logic easy to read and test in isolation.

## Known issues

- Move generation assumes an empty board, so it does not account for
  captures, checks, checkmate, castling, or blocking pieces — it is a
  movement-pattern showcase, not a full chess engine.
- `data/users.json` and `data/activity_log.json` are plain local
  files with no locking, so concurrent writes from multiple processes
  at the exact same moment could race. Fine for a single-user CLI,
  not for concurrent multi-user use.
- The in-memory `_id_counter` on `Piece`/`User` resets every time the
  program restarts, so IDs are only unique within a single run/process.

## Git workflow

Suggested branching model for the team:

- `main` — always deployable
- `feature/piece-models`, `feature/auth`, `feature/cli`, `feature/tests`
  — one branch per teammate/feature, merged via pull request into `main`
