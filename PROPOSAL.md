# Project Proposal: TaskFlow (CLI Project Management Tool)

## Problem statement
Small teams and freelancers frequently juggle multiple projects and
tasks without needing (or wanting) a heavyweight web app. TaskFlow is a
command-line tool that lets a team register accounts, log in securely,
create projects with due dates, and assign/track tasks within those
projects — all persisted locally as JSON so it works offline and needs
no server.

## Target users
- **User** (default role): manages their own projects and completes
  tasks assigned to them.
- **Admin**: everything a User can do, plus visibility into all users
  and override access to any project or task (e.g. for cleanup or
  dispute resolution).

## Core features
1. Account registration and login with hashed passwords.
2. Role-based access control (admin vs. user).
3. Create / list / delete projects (with due dates and overdue flags).
4. Create / list / complete tasks, assigned to a specific user.
5. Both a scriptable CLI (`argparse` subcommands) and an interactive,
   menu-driven mode for exploration.
6. All data persisted as JSON; corrupted/missing files degrade
   gracefully instead of crashing the app.
7. Action audit log (`data/activity.log`) written via a decorator.

## Entities (2+ required)
- **User** (inherits from a `Person` base class) — name, email,
  username, role, password hash + salt.
- **Project** — title, description, due date, owner.
- **Task** — title, status, assignee, parent project.

Relationships: one User owns many Projects; one Project has many Tasks.

## File / database storage plan
JSON files under `data/`: `users.json`, `projects.json`, `tasks.json`,
`session.json` (tracks who is currently logged in between separate CLI
invocations), and `activity.log` (plain-text audit trail). Handled by a
generic `utils/storage.py` load/save layer plus per-entity repository
classes (`utils/repository.py`) that expose `all()`, `find_by_id()`,
`add()`, etc.

## Authentication strategy
- Passwords hashed with PBKDF2-HMAC-SHA256 (100,000 iterations) and a
  random per-user salt, using only the Python standard library
  (`hashlib`, `os.urandom`) — no plaintext password is ever written to
  disk.
- `Session` object (`utils/auth.py`) exposes `register`, `login`,
  `logout`, and tracks `current_user`.
- `@login_required` and `@admin_required` decorators
  (`utils/decorators.py`) guard command handlers declaratively.

## Git workflow plan
- `main` is the protected, always-working branch.
- Feature branches per unit of work: `feature/user-auth`,
  `feature/project-crud`, `feature/task-crud`, `feature/cli-menu`,
  `feature/tests`.
- Pull requests require at least one teammate review before merge.
- Conventional commit messages (`feat:`, `fix:`, `docs:`, `test:`).

## Project management tracking
Trello board with columns To Do / In Progress / Done; one card per
feature area (auth, project CRUD, task CRUD, decorators/logging,
interactive menu, unit tests, documentation), assigned to individual
team members.

## Planned classes
- `Person` (base) → `User`
- `Project`
- `Task`
- `UserRepository`, `ProjectRepository`, `TaskRepository`
- `Session` (auth/session management)
