# TaskFlow — Group Work Split & Presentation Plan

This splits the TaskFlow codebase four ways along natural module
boundaries, so each person owns a coherent slice they can explain,
defend, and demo end-to-end. Swap names in for the placeholders below.

**Presentation order:** Member 1 → 2 → 3 → 4 (each builds on the last —
auth, then data, then behavior, then the finished experience + process).
Suggested time: **6–8 minutes per person** + questions.

---

## Member 1 — Domain Models & Authentication
**Placeholder: [Samuel Gitau]**

### Files owned
- `models/person.py`
- `models/user.py`
- `utils/auth.py`
- `utils/decorators.py`

### What to present
- Walk through `Person` as the base class and `User(Person)` as the
  concrete subclass — this is the **inheritance** requirement.
- Show how every attribute is private (`_name`, `_email`, `_role`, …)
  and only reachable through validated `@property` getters/setters —
  this is the **encapsulation** requirement. Live-demo what happens if
  you try to set an invalid email or an invalid role.
- Explain the password security model: PBKDF2-HMAC-SHA256 with a
  random per-user salt via the standard library `hashlib` — no
  plaintext password ever touches disk. Open `data/users.json` after a
  live registration to prove it.
- Explain `Session` (`utils/auth.py`): register / login / logout, and
  why the logged-in username is persisted to `session.json` so a login
  survives between separate CLI process runs.
- Explain the three decorators in `decorators.py`
  (`@login_required`, `@admin_required`, `@log_action`) and demo one
  command with and without being logged in / being an admin.

### Be ready to defend
- *Why hash with PBKDF2 instead of plain `hashlib.sha256`?* (salting +
  iteration count defends against rainbow tables and brute force.)
- *Why store the session as a username, not a token or the password?*
- *Why does `Person` exist at all if only `User` uses it?* (demonstrates
  inheritance and leaves room for future subclasses, e.g. `Guest`.)

---

## Member 2 — Data Persistence & Repositories
**Placeholder: [Name 2]**

### Files owned
- `utils/storage.py`
- `utils/repository.py`
- `models/project.py` (persistence-relevant parts: `to_dict`/`from_dict`)
- `data/` folder structure (`users.json`, `projects.json`, `tasks.json`,
  `session.json`, `activity.log`)

### What to present
- Explain `load_json` / `save_json` in `storage.py`: how a missing file
  returns an empty list instead of crashing, and how a corrupted file
  is caught (`try/except` around `json.JSONDecodeError`) and logged as
  a warning rather than taking down the app. Demo it by corrupting a
  JSON file live and re-running the app.
- Explain the repository classes (`UserRepository`, `ProjectRepository`,
  `TaskRepository`): why business logic never touches raw JSON
  directly, only these `all()` / `find_by_id()` / `add()` methods.
- Explain the class-attribute id counters (`_id_counter`) on `User`,
  `Project`, and `Task` — how they auto-increment on creation and stay
  correctly ahead of existing data when records are reloaded from disk.
- Show the one-to-many relationships in the data itself: a project's
  `owner_username` links to a `User`, and a task's `project_id` links
  to a `Project`.

### Be ready to defend
- *Why JSON instead of a real database?* (matches the assignment scope;
  trade-off is no concurrent-write safety — a real product would move
  to SQLite/Postgres.)
- *Why repositories instead of each command reading/writing JSON
  directly?* (single responsibility, testability, one place to change
  storage format later.)
- *What happens if two processes write at the same time?* (last-write-
  wins via `os.replace`; acceptable for a single-user local CLI.)

---

## Member 3 — CLI Commands & Business Logic
**Placeholder: [Name 3]**

### Files owned
- `models/task.py`
- `cli/commands.py`
- `main.py` (argparse subcommands + dispatch)

### What to present
- Walk through `main.py`: how `argparse` defines each subcommand
  (`register`, `login`, `add-project`, `add-task`, `complete-task`,
  etc.) and routes to a handler in `commands.py`.
- Explain why the command handlers are shared between the scriptable
  CLI and the interactive menu (Member 4's territory) instead of
  duplicated — one function, two entry points.
- Demo the permission rules in `commands.py`: a task can only be
  completed by its assignee or an admin; a project can only be deleted
  by its owner or an admin. Show the code and demo both the success and
  denied paths live.
- Explain the `Task` model's status validation (`todo` / `in_progress`
  / `done`) and the `mark_complete()` method.
- Show input validation end-to-end: an invalid due date or empty title
  raises a `ValueError` that's caught and reported cleanly, never a raw
  traceback.

### Be ready to defend
- *Why argparse subcommands instead of one giant `if/elif` on raw
  `sys.argv`?* (built-in `--help`, type checking, cleaner errors.)
- *Why can an admin override task/project ownership rules?* (support/
  moderation use case, discussed and scoped in the proposal.)
- *Why validate inside the model's setters instead of in the CLI
  layer?* (a `Task` can never exist in an invalid state, no matter what
  code creates it — defends the object, not just the command.)

---

## Member 4 — Interactive UX, Testing, and Process
**Placeholder: [Name 4]**

### Files owned
- `cli/menu.py`
- `tests/test_models.py`
- `tests/test_cli_logic.py`
- `README.md`, `PROPOSAL.md`
- Git workflow + Trello/Jira board (process, not code)

### What to present
- Live-demo the interactive menu mode (`python main.py` with no
  arguments): registration, login, and the role-aware menu (show that
  an admin sees an extra "List users" option a regular user doesn't).
- Walk through the test suite: 17 tests covering model validation
  (rejecting bad email/date/status/role), password hashing/verification,
  serialization round-trips, and full CLI flows (register → login →
  add project → add task → complete task) using an isolated temp data
  directory so tests never touch real data. Run `python -m unittest
  discover -s tests -v` live.
- Explain the Git workflow: `main` branch protected, one feature branch
  per module (mapping roughly to Members 1–3's slices above), PR review
  before merge, conventional commit messages.
- Show the Trello/Jira board and how cards were assigned and moved
  across To Do / In Progress / Done.

### Be ready to defend
- *Why mock/isolate the data directory in tests instead of testing
  against real `data/*.json`?* (tests must be repeatable and never
  corrupt real user data.)
- *Why offer both an interactive menu and argparse subcommands instead
  of just one?* (menu for exploration/new users, subcommands for
  scripting/automation — same underlying command functions either way.)
- *What would you test next if you had more time?* (concurrent writes,
  larger datasets, CLI argument edge cases.)

---

## Presentation Checklist (whole team)
- [ ] Each member can run their slice of the app live, not just show slides.
- [ ] Each member can explain **one specific line of code** that
      demonstrates encapsulation, inheritance, or a decorator in their
      section — the graders will likely ask "show me OOP in your code."
- [ ] The team can explain how the four slices connect end-to-end:
      register (M1) → data saved (M2) → command executed (M3) → seen in
      the menu and covered by a test (M4).
- [ ] Bring the Trello/Jira board link and recent Git history (feature
      branches + merged PRs) to show, not just describe.
