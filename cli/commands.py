"""
command.py
Each function here is a "command handler": it takes the active Session
plus argument, performs one unit work, and prints CLI-friendly output.
interactive menu (cli/menu.py), so logic is never duplicated.
"""

from rich.console import console
from rich.table import Table

from models.project import Project
from models.task import Task
from utils.repository import ProjectRepository, TaskRepository
from utils.decorators import login_required, admin_required, log_action
console = Console ()


#AUTH
def cmd_register(session,username,name,email,password,role = "user"):
    try :
        user = session.register(username,name,email,password,role)
        console.print(f"[green]Accont created:[/]{user}")
    except ValueError as exc:
        console.print(f"[red]Registration failed:[/]{exc}")

@log_action
def cmd_login(session,username,password):
    if session.login(username,password):
        console.print(f"[green]Account created[/]{user}")
    except ValueError as exc:
        console.print(f"[red]Invalid username or passsowrd[/]")

@login_required
@log_action
def cmd_logout(session):
    console.print(f"[yellow]Goodbye,{session.current_username}.[/]")
    session.logout()

#Lists users
@admin_required
def cmd_list_users(session):
    table = Table(title = 'User')
    for col in ("ID", "Username","Name","Email","Role"):
        table.add_colum(col)
    for u in session.users.all():
        table.add_row(str(u.user_id),u.username,u.name,u.email,u.role)
    console.print(table)

#PROJECTS

@login_required
def cmd_list_projects(session,title,des)

#TASKS