## Linux/WSL etc.
1. `git clone --branch improved_time_complexity git@github.com:kwantton/MinesweeperBot.git`
2. `cd MinesweeperBot` (or whatever is the name of the folder that you just pulled)
('venv/' is in '.gitignore', as it shouldn't be pulled from GitHub. If you have `venv` for whatever reason in 'MinesweeperBot' folder, `rm -rf venv`, then follow below)

If you'd like to use a virtual environment (just for pygame, really, in this case):

3. `python -m venv venv` or `python3 -m venv venv`, or whatever works in your case
4. `source venv/bin/activate`

you should see `(venv)` at the start of your shell row, (of course, you can do this also not in a virtual environment if you want to)

5. `pip install -r requirements.txt`
For what: this installs `pygame` to your venv. At the moment (12.10.2024), `constraint` is not needed, I'm planning to use it for test result verification (for solving linear equations to see if my algorithm works. That requires more test specifications since my algorithm only prints out those variables that are always 1 or always 0, so work is to be done to make that even possible at the moment)
6. run 'botGame.py' (python) which has instructions at the bottom of the game, or 'CSP_solver.py' to run the tests of 'CSP_solver' class
