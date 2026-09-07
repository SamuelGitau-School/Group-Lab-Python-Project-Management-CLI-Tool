#!/usr/bin/env python3
"""
main.py
TaskFlow - a CLI project management tool.

Usage:
    python main.py                              -> interactive menu mode
    python main.py register -u bob -n "Bob" -e bob@x.com -p secret
    python main.py login -u bob -p secret
    python main.py add-project -t "Website" -d "Redo homepage" --due 2026-12-01
    python main.py list-projects [--mine]
    python main.py add-task --project 1 -t "Design mockups" -a bob
    python main.py list-tasks [--project 1] [--mine]
    python main.py complete-task --id 3
    python main.py list-users            (admin only)
    python main.py logout
"""

import argparse
import sys

from utils.auth import Session
from cli import commands as c
from cli import menu


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taskflow", description="TaskFlow CLI project management tool")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("register", help="Create a new account")
    p.add_argument("-u", "--username", required=True)
    p.add_argument("-n", "--name", required=True)
    p.add_argument("-e", "--email", required=True)
    p.add_argument("-p", "--password", required=True)
    p.add_argument("--role", default="user", choices=["user", "admin"])

    p = sub.add_parser("login", help="Log in and persist the session")
    p.add_argument("-u", "--username", required=True)
    p.add_argument("-p", "--password", required=True)

    sub.add_parser("logout", help="Log out of the current session")
    sub.add_parser("list-users", help="List all users (admin only)")

    p = sub.add_parser("add-project", help="Create a project")
    p.add_argument("-t", "--title", required=True)
    p.add_argument("-d", "--description", default="")
    p.add_argument("--due", required=True, help="YYYY-MM-DD")

    p = sub.add_parser("list-projects", help="List projects")
    p.add_argument("--mine", action="store_true")

    p = sub.add_parser("delete-project", help="Delete a project you own")
    p.add_argument("--id", type=int, required=True, dest="project_id")

    p = sub.add_parser("add-task", help="Add a task to a project")
    p.add_argument("--project", type=int, required=True, dest="project_id")
    p.add_argument("-t", "--title", required=True)
    p.add_argument("-a", "--assign-to", required=True, dest="assigned_to")

    p = sub.add_parser("list-tasks", help="List tasks")
    p.add_argument("--project", type=int, dest="project_id", default=None)
    p.add_argument("--mine", action="store_true")

    p = sub.add_parser("complete-task", help="Mark a task complete")
    p.add_argument("--id", type=int, required=True, dest="task_id")

    return parser


def dispatch(args, session: Session) -> None:
    if args.command == "register":
        c.cmd_register(session, args.username, args.name, args.email, args.password, args.role)
    elif args.command == "login":
        c.cmd_login(session, args.username, args.password)
    elif args.command == "logout":
        c.cmd_logout(session)
    elif args.command == "list-users":
        c.cmd_list_users(session)
    elif args.command == "add-project":
        c.cmd_add_project(session, args.title, args.description, args.due)
    elif args.command == "list-projects":
        c.cmd_list_projects(session, mine_only=args.mine)
    elif args.command == "delete-project":
        c.cmd_delete_project(session, args.project_id)
    elif args.command == "add-task":
        c.cmd_add_task(session, args.project_id, args.title, args.assigned_to)
    elif args.command == "list-tasks":
        c.cmd_list_tasks(session, project_id=args.project_id, mine_only=args.mine)
    elif args.command == "complete-task":
        c.cmd_complete_task(session, args.task_id)


def main():
    parser = build_parser()
    args = parser.parse_args()
    session = Session()

    if args.command is None:
        # No subcommand given -> drop into interactive menu mode
        menu.run(session)
        return

    try:
        dispatch(args, session)
    except ValueError as exc:
        print(f"[error] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
