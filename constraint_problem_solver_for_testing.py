from constraint import Problem                          # this could be used (not done at the moment if grey) to solve groups of CSP-equations (CSP = constraint satisfaction problem)

def get_all_variables_from(eqs:list) -> list:
    variables = set()
    for vars, value in eqs:
        for var in vars:
            variables.add(var)
    return variables

def check_if_solutions_were_missed_in_lost_game(equations:list, 
        remaining_mines_in_map:int, all_vars_in_remaining_map:set, x:int, y:int):
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
    '''
    problem = Problem()         # THIS IS where the problem solving (checking) happens

    def check_for_absolutely_solved_vars():
        # Analyze solutions to find consistently 0 or 1 variables
        variable_count = {var: [0, 0] for var in all_vars_from_eqs}  # [count_0, count_1]

        # count how many times 0 and how many times 1 each var was, just like in CSP_solver
        for solution in solutions:
            for var, value in solution.items():
                variable_count[var][value] += 1

        # just like I did in CSP_solver, identify variables that are always 0 or 1 in ALL possible solutions (alt solutions as I call them)
        always_zero = [var for var, counts in variable_count.items() if counts[1] == 0]
        always_one = [var for var, counts in variable_count.items() if counts[0] == 0]

        # for checking all possible solutions (check that the verifier is working)
        # print("Total Solutions:", len(solutions))
        # for solution in solutions:
        #     print(solution)

        print("Variables always 0:", always_zero)
        print("Variables always 1:", always_one)
        

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

    check_for_absolutely_solved_vars()
