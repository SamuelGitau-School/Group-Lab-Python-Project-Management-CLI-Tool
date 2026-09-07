# TaskFlow — Code Defense Slide Outline

## Slide 1 — Title
**TaskFlow: A CLI Project Management Tool**
Team names · course/lab name · date

## Slide 2 — The Problem
- Small teams need lightweight project/task tracking without a full web app
- Solution: a local, offline-first CLI with per-user logins and JSON persistence
- Two roles: **User** (own projects/tasks) and **Admin** (oversight)

## Slide 3 — Architecture at a Glance
- One diagram or file tree: `models/ → utils/ → cli/ → main.py`
- One sentence per layer: models = data + rules, utils = auth/storage,
  cli = commands + menu, main.py = entry point
- Call out: **same command functions power both the scriptable CLI and
  the interactive menu** — no duplicated logic

---

### Member 1 — Models & Authentication

## Slide 4 — Inheritance & Encapsulation
- `Person` (base) → `User(Person)`
- All attributes private (`_email`, `_role`, …), only touched through
  validated `@property` setters
- **Live demo:** try to set an invalid email/role, show the `ValueError`

## Slide 5 — Authentication & Sessions
- PBKDF2-HMAC-SHA256 + random per-user salt (stdlib `hashlib`) — no
  plaintext password ever stored
- **Live demo:** register a user, open `data/users.json`, point at the hash
- `Session` persists the logged-in *username* (not a password) to
  `session.json` so login survives across separate CLI runs
- `@login_required` / `@admin_required` / `@log_action` decorators

---

### Member 2 — Persistence & Repositories
- {**Insight of what is happening**}

### Member 3 — CLI Commands & Business Logic
- {**Insight of what is happening**}

### Member 4 — UX, Testing & Process
- {**Insight of what is happening**}