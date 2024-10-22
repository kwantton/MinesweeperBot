'''
FOR TESTING! When you run the games (run 'botGame.py' python code) in mode 'i' + 'a' (infinitely;
a new game will start once the previous has been finished and once it has been checked here!), the number of 
cases where solutions where found from here (enumerating all possible answers) that were NOT found by
the solver logic I built (i.e. 'missing logic'), are recorded in botGame.py,
and drawn on the screen: 'missing logic: 0' at start, written in green. The count would turn
to 1 or more in cases where missing logic was found (and text would turn to red c:)

To use this, you must have 'logic_testing_on = True' in botGame.py when you run it (go to bottom of 'botGame.py')

Note! When 'self.time_limit = x' in 'CSP_solver.py' is too small, it's possible that logic solving in CSP_solver is inadequate
(the timer will stop 'traverse()' if the time in seconds is exceeded). In those cases, however, running this
test would also take a ridicilous amount of time, as this is not a quick way to check for missing logic.
'''
from constraint import Problem                          # this could be used (not done at the moment if grey) to solve groups of CSP-equations (CSP = constraint satisfaction problem)
from time import sleep

def get_all_variables_from(eqs:list) -> list:
    variables = set()
    for vars, value in eqs:
        for var in vars:
            variables.add(var)
    return variables

def check_if_solutions_were_missed_in_lost_game(equations:list, 
        remaining_mines_in_map:int, all_vars_in_remaining_map:set, x:int, y:int) -> int:
    '''
    for the bunch of equations that were present when the mine was clicked as a result of a guess,
    check if one or more variables in the equations actually COULD have been solved (instead of guessing).
    - constraints:
        - every var is 0 or 1
        (- sum of eqs in candidate ≤ remaining_mines_in_map)
        (- sum of all eqs in candidate solution + n_uu_cells ≥ remaining_mines_in_map)
        - HOWEVER! I could just add the following:
        `sum(all_unclicked) = remaining_mines_in_map`
        Problem: that can be a HUGE equation! I'll have to find out if that will work...
    RETURNS: +1 if logic was missed. This count is then recorded in 'botGame'.
    '''
    problem = Problem()         # THIS IS where the problem solving (checking) happens

    def check_for_absolutely_solved_vars() -> int:
        '''
        checks if one or more vars were always 0 or always 1 (=solved). If were, returns 1
        '''
        # just like in CSP_solver, var : [n_0s, n_1s] for every variable
        variable_count = {var: [0, 0] for var in all_vars_from_eqs}

        # count how many times 0 and how many times 1 each var was, just like in CSP_solver
        for solution in solutions:
            for var, value in solution.items():
                variable_count[var][value] += 1

        # just like I did in CSP_solver, identify variables that are always 0 or 1 in ALL possible solutions (alt solutions as I call them)
        always_zero = [var for var, counts in variable_count.items() if counts[1] == 0]
        always_one = [var for var, counts in variable_count.items() if counts[0] == 0]

        # for checking all possible solutions (check that the verifier is working)
        print("number of possible solutions TOTAL:", len(solutions))
        # for checking all possible solutions (check that the verifier is working)
        # for solution in solutions:
        #     print(solution)

        print("Variables always 0:", always_zero)
        print("Variables always 1:", always_one)

        if len(always_one) > 0 or len(always_zero) > 0:
            print('MISSING LOGIC FOUND! sleep 60')
            sleep(60)
            return 1

    print('check_if_solutions_were_missed_in_lost_game()')
    all_vars_from_eqs = list(get_all_variables_from(equations))
    print('- all_vars:', all_vars_from_eqs)
    # print('- len(all_vars_from_eqs):', len(all_vars_from_eqs))
    n_unclicked_pre_loss = len(all_vars_in_remaining_map) + 1                   # why + 1; because after clicking a mine, it's also no longer unclicked. I want the situation BEFORE clicking the mine. Gotta be careful here! Checking: look at the game and add 1 - it's correct.
    # print('- n_unclicked BEFORE hitting mine:', n_unclicked_pre_loss)
    problem.addVariables(all_vars_from_eqs, [0,1])                              # every var is 0 or 1, this is how it's set

    # Function to add constraints based on each equation
    def add_equations_to_problem(problem, equations):
        for vars_in_eq, sum_value in equations:
            # Define a lambda that checks if the sum of the variables equals the given sum_value
            problem.addConstraint(
                lambda *args, sum_value=sum_value: sum(args) == sum_value, vars_in_eq
            )

    # Add all equations as constraints
    add_equations_to_problem(problem, equations)

    # Get possible solutions
    solutions = problem.getSolutions()

    # print('-solutions:', solutions)

    result = check_for_absolutely_solved_vars()
    if result == 1:
        return result
    return 0
