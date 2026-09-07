# TaskFlow — CLI Project Management Tool

TaskFlow is a command-line project management tool built for the group lab.
Users register an account, log in, and manage **Projects** and **Tasks**
that persist between runs as JSON files. It supports two roles
(`admin` and `user`) and can be driven either as a scriptable CLI
(`argparse` subcommands) or as an interactive menu.

## Problem it solves

Small teams often need a lightweight way to track "who owns what" without
standing up a full web app. TaskFlow gives each user their own login,
lets them create projects with due dates, break projects into tasks
assigned to teammates, and mark work done — all from the terminal, with
data saved locally in plain JSON.

## Target users

- **User** — creates their own projects, adds tasks, completes tasks
  assigned to them.
- **Admin** — everything a User can do, plus viewing all registered
  users and managing any project/task regardless of owner.

## Entities

| Entity  | Key attributes                                   |
|---------|---------------------------------------------------|
| User    | user_id, username, name, email, role, password_hash, salt |
| Project | project_id, title, description, due_date, owner_username |
| Task    | task_id, title, status, assigned_to, project_id  |

Relationships: **User → many Projects**, **Project → many Tasks**.

## Architecture

```
taskflow/
├── main.py              # CLI entry point (argparse) + interactive fallback
├── requirements.txt
├── cli/
│   ├── commands.py      # command handlers shared by argparse & menu
│   └── menu.py          # interactive, menu-driven CLI flow
├── models/
│   ├── person.py        # Person (base class)
│   ├── user.py          # User(Person) — auth, hashing, roles
│   ├── project.py       # Project
│   └── task.py          # Task
├── utils/
│   ├── storage.py        # generic JSON load/save, handles missing/bad files
│   ├── repository.py     # UserRepository / ProjectRepository / TaskRepository
│   ├── auth.py            # Session: login/register/logout, persisted session
│   ├── decorators.py      # @login_required, @admin_required, @log_action
│   └── validators.py      # input validation helpers for prompts
├── data/                  # JSON persistence + activity.log (created at runtime)
└── tests/
    ├── test_models.py
    └── test_cli_logic.py
```

### OOP principles demonstrated

- **Inheritance**: `User` extends `Person` (shared name/email validation).
- **Encapsulation**: all model attributes are private (`_prefixed`) and
  exposed only through validated `@property` getters/setters (e.g. you
  cannot set an invalid email, an invalid task status, or an invalid role).
- **Classes & collaboration**: `User`, `Project`, and `Task` are linked
  by id (`owner_username`, `project_id`, `assigned_to`) and managed
  through dedicated repository classes with class-attribute id counters.
- **Decorators**: `@login_required`, `@admin_required`, and `@log_action`
  wrap command handlers to enforce authentication/authorization and
  write an audit trail — without cluttering business logic.

### Authentication strategy

- Passwords are **never stored in plaintext**. Each user gets a random
  16-byte salt; the password is hashed with PBKDF2-HMAC-SHA256
  (100,000 iterations) via the Python standard library (`hashlib`).
- `data/session.json` stores only the *currently logged-in username*
  (not a password) so that a session persists between separate CLI
  invocations, e.g. `login` in one command and `add-project` in the
  next — the way real CLIs like `gh` or `aws` behave.
- Role-based access: `admin` vs `user`, enforced via `@admin_required`.

### Persistence

All data is stored as JSON under `data/`: `users.json`, `projects.json`,
`tasks.json`, plus `session.json` (current login) and `activity.log`
(audit trail written by `@log_action`). `utils/storage.py` gracefully
handles a missing or corrupted file by starting with an empty dataset
instead of crashing.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Interactive mode (menus)

```bash
python main.py
```

### Scriptable mode (argparse subcommands)

```bash
# Accounts
python main.py register -u bob -n "Bob Builder" -e bob@example.com -p secret123
python main.py register -u admin -n "Admin" -e admin@example.com -p adminpw --role admin
python main.py login -u bob -p secret123
python main.py logout

# Projects
python main.py add-project -t "Website Revamp" -d "Redo the homepage" --due 2026-12-01
python main.py list-projects [--mine]
python main.py delete-project --id 1

# Tasks
python main.py add-task --project 1 -t "Design mockups" -a bob
python main.py list-tasks [--project 1] [--mine]
python main.py complete-task --id 1

# Admin only
python main.py list-users
```

## Running tests

```bash
python -m unittest discover -s tests -v
```

Tests cover model validation (bad email/date/status/role rejected),
password hashing/verification, JSON serialization round-trips, and the
CLI command layer (register/login flow, permission checks, task
ownership rules) using a temporary, isolated data directory so tests
never touch real data.

## Git workflow

- `main` branch is always deployable.
- One feature branch per entity/feature, e.g. `feature/user-auth`,
  `feature/project-crud`, `feature/task-crud`, `feature/cli-menu`.
- Pull requests reviewed by at least one teammate before merging.
- Commit messages follow `type: short description` (e.g.
  `feat: add password hashing to User`, `fix: handle missing json file`).

## Project management

Work was tracked on a Trello/Jira board with three columns
(To Do / In Progress / Done) and one card per feature listed above
(auth, project CRUD, task CRUD, decorators, CLI menu, tests, docs).

## Team

_Add your team members' names and GitHub handles here before submitting._
