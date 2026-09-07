### CREATING A VIRTUAL ENVIRONMENT
From inside the taskflow folder, run `python3 -m venv venv`, then activate it: `source venv/bin/activate`.
You'll see `(venv)` appear in your prompt once it's active.

### INSTALLING DEPENDACIES
With the venv active, run `pip install -r requirements.txt`. 
This installs `rich`, the only external package the app needs, for the styled tables and colored output.

### RUN THE PROJECT(LAUNCH INTERACTIVEMODE)
Run `python main.py` with no arguments.
This drops you into the menu-driven flow: register an account, log in, and click through numbered options to create projects, add tasks, and mark things complete.
**OR RUN SCRIPTABLE COMMANDS**
Instead of the menu, you can drive everything with subcommands, e.g. `python main.py register -u bob -n "Bob" -e bob@example.com -p secret123`,
then `python main.py login -u bob -p secret123`, then `python main.py add-project -t "Website" -d "Redo homepage" --due 2026-12-01`.
Run `python main.py --help` to see every subcommand.

### TO RUN TEST
{~Will be added after test is added}~