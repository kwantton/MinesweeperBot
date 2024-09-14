'''to-do: 
- [isn't this done now in 'update_unique_equation'?] for solved variables, check each of them in factor_one_solve. This should be taken into account also when considering new equations; don't save unsolved bootleg duplicates as 'new' equations if in reality they are the unsolved versions of already solved equations
- in 'factor_one_solve', an easy way to check if subtracting the subset from the larger set is correct is as follows: if you end up with a+b+.... < 0, the subtraction was WRONG - something was wrong in the code itself. Why; because x ∈{0,1} for all cells x, and because I'm always subtracting a subset from a larger or equally sized set. Therefore, as every element of each set is 0 or 1, it is not possible to end up with a negative result for the resulting equation. For example: a+b+c = 1, a+b+c+d = 2 -> d = 1. The resulting equation can never have a negative value, if every element of the subset is found in the larger set, and every element x ∈{0,1} for all cells x!
- destructuring in case of non-tuple variable names will not work; beware in the examples! (variables like 'a', 'b' may not work, when you attempt to destructure them like '(x,y), value', for example)

done:
- 'filter_out_solved_variables' was faulty
- If you end up with 'a+b+c+... = 0' as the result equation, assign every one of those variables as 0 (this is CSP where the constraint is that x ∈{0,1} for all cells x)
- clear the one-round temporary storages after use (after each round); 'self.variables_and_sum_to_DELETE_...' and 'self.variables_and_sum_to_ADD...'
- at the end of 'factor_one_solve', update all equations with the variables that were solved ('update_info...')
- update 'variable_to_equations' after solving
- update self.numberOfVariables_to_equations, as you update old equations to ones with solved variables taken into account
- create a function for updating all necessary info ('update_info...', 'update_equation...')

'''

# NB! 'sum' = the label of the cell in minesweeer map (the number seen on the cell)
# Searching: (1) 'variable_to_equations'; get all equations that contain a specific 'variable' as key, (2) self.json: get all the info about an equation; {equation : info_structures_here}. Together, these two enable efficient search of info about any equation based on the variable included in the equation
class CSP_solver:
    def __init__(self):

        self.variables = set()                              # all variables.
        self.unique_equations = set()                       # { ((var1, var2, ..), sum_of_mines_in_vars), (...) }. Each var (variable) has format (x,y) of that cell's location; cell with a number label 1...8 = var. Here, I want uniqe EQUATIONS, not unique LOCATIONS, and therefore origin-(x,y) is not stored here. It's possible to get the same equation for example from two different sides, and via multiple different calculation routes, and it's of course possible to mistakenly try to add the same equation multiple times; that's another reason to use a set() here, the main reason being fast search from this hashed set.        
        self.solved_variables = set()                       # ((x,y), value)
        self.variable_to_equations = dict()                 # { variable_a:set(equation5, equation12, equation4,...), variable_b:set(equation3, equation4...)}
        self.numberOfVariables_to_equations = {             # { numberOfVariables : set(equation1, equation2, ...) }; each key of this dict is integer x, and x's values are all equations with x number of variables. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables; if all the variables in the shorter equation are found in the longer equation, then perform subtraction to get rid of those varibles in the longer equation (linear equation solving), then save the formed result equation to 'self.unique_equations' and 'self.numberOfVariables_to_equations'.
            x:set() for x in range(0, 8+1)                  # Why up to 8? Because a single '1' cell, resulting from a forced guess in the middle of unclicked cells, has 8 neighbours, hence 8 variables in the equation for that '1' cell; some of these neighbours can be shared with other cells in case of a compulsory guess having been made (the lonely '1' in the middle would be the guess then, obviously). NB! It's possible that when all variables in a given equation have just been solved, all are canceled out, and at that point the length of the equation (i.e. the number of variables) becomes 0; that's why I'm starting from 0.
        }                                                   # { numberOfVariables : set(equation1, equation2, ...) }; all equations with numberOfVariables = x. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables.
        
        self.variables_and_sum_to_DELETE_from_self_numberOfVariables_to_equations_after_iteration = set()   # needed to avoid error 'Set changed size during iteration'; this set is needed as one-round-lived storage for 'self.factor_one_solve()' since there is a loop that involves these equations that should be removed later; therefore, they cannot be removed from 'self.numberOfVariables_to_equations' during iteration, but instead they have to be temporarily stored here, and removed AFTER the iteration round.
        self.variables_and_sum_to_ADD_to_self_numberOfVariables_to_equations_after_iteration = set()        # same as above; needed to avoid error of 'Set changed size during iteration'

    # NB! This is called, when adding new equations for the first time, AND after finding new variables. Hence, sometimes the 'self.update_equation(equation)' is necessary.
    def add_equations_if_new(self, equations:list) -> None:                             # equations = [(x, y, ((x1, y1), (x2, y2), ...), summa), ...]; so each equation is a tuple of of x, y, unflagged unclicked neighbours (coordinates; unique variables, that is!), and the label of the cell (1,2,...8)
        for equation in equations:                                                      # (x,y,(variables),sum_of_variables)
            x, y, variables, summa = self.update_equation(equation)                     # both updates, IF NECESSARY, 'self.unique_equations' (removes the old one, adds the shorter one), AND returns the new one right away
            if (variables, summa) not in self.unique_equations:                         # can't hash sets; 'variables' has to be a tuple!
                variable_count = 0
                for variable in variables:
                    variable_count += 1
                    if variable not in self.variable_to_equations:
                        self.variable_to_equations[variable] = set()
                    self.variable_to_equations[variable].add((variables, summa))        # the purpose of {variable : equations} is to be able to find all equations that have the variable
                self.unique_equations.add((variables, summa))
                if variable_count not in self.numberOfVariables_to_equations:
                    self.numberOfVariables_to_equations[variable_count] = set()
                self.numberOfVariables_to_equations[variable_count].add((variables, summa)) # same format as in 'self.unique_equations'; without (x,y) that is
                for variable in variables:
                    self.variables.add(variable)

    # this is used in (1) 'self.add_equations_if_new()' and in (2) 'self.factor_one_solve()' (3) 'self.update_info_after_solving_new_variable'; (1) do not add 'new' equations that have been already (partially) solved; that is, take into account the fact that some variables have been solved already (2) TO-DO
    # (1) in all equations where solved variables exist, reduce for solved variables (2) update the reduced form to 'self.unique_equations' (3) update to 'self.numberOfVariables_to_equations' (4) others? TO-DO, CHECK!
    def update_equation(self, equation:tuple) -> None:                                      # equation = ( (var1, var2, ...), sum_of_variables). There's no origin (x,y) here, because all of those are unique, and irrelevant here!
        x, y, original_vars, original_summa = equation
        unsolved_variables, sum_of_solved_vars = self.filter_out_solved_variables(original_vars)
        if len(unsolved_variables) != len(original_vars):                                   # True, if one or more variables in 'original_vars' had indeed been solved already; in that case we need to update all related information: (1) 'self.unique_equations', (2) 'self.numberOfVariables_to_equations', (3) DONE AT THE END OF 'factor_one_solve': 'self.variable_to_equations'. Otherwise 'factor_one_solve' will have old info and will not work.
            if (original_vars, original_summa) in self.unique_equations:
                self.unique_equations.remove((original_vars, original_summa))
            if len(original_vars) in self.numberOfVariables_to_equations:
                if (original_vars, original_summa) in self.numberOfVariables_to_equations[len(original_vars)]:
                    self.variables_and_sum_to_DELETE_from_self_numberOfVariables_to_equations_after_iteration.add((original_vars, original_summa))
            
            if len(unsolved_variables) == 1:
                self.solved_variables.add((unsolved_variables[0], original_summa-sum_of_solved_vars))
            else:
                self.unique_equations.add((unsolved_variables, original_summa-sum_of_solved_vars))
            
            # if (unsolved_variables, summa-sum_of_solved_vars) not in self.numberOfVariables_to_equations[len(unsolved_variables)]:      # TO-DO: why is there a key error occasionally? I had to comment this out. Of course, technically this is a redundant check, since we're adding to a set, but the check would be useful for showing the logic AND useful for debugging
            self.variables_and_sum_to_ADD_to_self_numberOfVariables_to_equations_after_iteration.add((unsolved_variables, original_summa-sum_of_solved_vars))
                #self.numberOfVariables_to_equations[len(unsolved_variables)].add((unsolved_variables, summa-sum_of_solved_vars))
            x = y = -1                                                                          # if information from already solved variables has been used to simplify equation, then this equation no longer has defnitivie single (x,y) origin from the minesweeper map; hence, mark it as (-1,-1).
        return [x, y, unsolved_variables, original_summa-sum_of_solved_vars]
     
    def modify_iterables_after_iterations_in_factor_one(self):                                                 
        for variables, summa in self.variables_and_sum_to_DELETE_from_self_numberOfVariables_to_equations_after_iteration:
            if (variables, summa) in self.numberOfVariables_to_equations[len(variables)]:
                self.numberOfVariables_to_equations[len(variables)].remove((variables, summa))  # to-do: without this check, key error sometimes without the check, unexpectedly. Figure out why
        self.variables_and_sum_to_DELETE_from_self_numberOfVariables_to_equations_after_iteration.clear()

        mark_these_as_solved_after_iteration = []                                               # (var, value). NB! I had to create this list again so that I don't run into the 'Set changed size during iteration' error. Ironically, this whole function was created to prevent that from happening!
        for variables, summa in self.variables_and_sum_to_ADD_to_self_numberOfVariables_to_equations_after_iteration:
            if summa == 0:                                                                      # for example, variables = (a,d), summa = 0 -> this means that a = 0, and d = 0
                for var in variables:
                    if (var,0) not in self.solved_variables:
                        mark_these_as_solved_after_iteration.append((var,0))
            elif len(variables) == 1:
                mark_these_as_solved_after_iteration.append((variables[0], summa))              # TO-DO: check if this ever happens (is this line needed here)
            else:                                                                               # we don't want equations like (('a','d'),0), as they would just cause more work in the 'self.factor_one_solve', as they provide no new information during subtractions with other equations
                self.numberOfVariables_to_equations[len(variables)].add((variables, summa))      
        self.variables_and_sum_to_ADD_to_self_numberOfVariables_to_equations_after_iteration.clear()
        for above_solved_var in mark_these_as_solved_after_iteration:
            self.mark_var_as_solved_and_update_related_info(above_solved_var)
        
    def filter_out_solved_variables(self, variables) -> tuple:
        unsolved_vars = []
        sum_of_solved_vars = 0
        for var in variables:
            # ((x,y), value). I can't know if it's 0 or 1, so I'm checking both. 'var' = (x,y) and each var is unique cell of the minesweeper map
            if (var, 0) not in self.solved_variables and (var, 1) not in self.solved_variables: # ((x,y), value), in 'self.solved_variables'
                unsolved_vars.append(var)
            elif (var, 1) in self.solved_variables:
                sum_of_solved_vars += 1
        return tuple(unsolved_vars), sum_of_solved_vars                                 # you can't hash sets or lists (not immutable), hence a tuple is returned instead for 'unsolved_vars'. Hashing of 'unsolved_variables' is needed in 'add_equations' from where this function is used.
    
    # NB! the 'rounds=1' is arbitrary, and is fun for testing (has never proven to solve anything extra, though, when higher than 1!). In 'botGame.py' I am calling one 'bot_move' per one press of key 'b' by the person running the program, and a part of each of these 'bot_move's is this 'factor_one_solve()' here. Therefore, for visualization and debugging purposes, I want to make it possible to advance one small step at a time; that's why I have the 'rounds=1' set by default. Also, performance-wise, there is no obvious way to tell if performing one or multiple of these rounds in a row is faster or not (on average; this depends on so many things, including the map itself!) without considering first if the simpler logic in 'bot_move' before this 'CSP_solver' has anything more to offer before this 'CSP_solver' is performed or not; so performance-wise, it's a bit of a (micro)mystery, at least yet, whether one should let this run for a longer time or not by default.
    def factor_one_binary_solve(self, how_many_rounds=1):                               # 'factor_one' here means that each variable has a factor of exactly one (or, to be exact, zero when it's not present), no more, for this solver (e.g. a+b+c=2, never a+2b+c=2 for example, since each minesweeper map cell has exactly one of each neighbour). This should be enough; there should not be a need to sum equations in my case!
        print('factor_one_solve():')
        equations_to_check_for_found_solutions = []
        subtractions_done = False                                                       # if no subtractions are done, it means that there are no different-sized equations that share a subset of variables (e.g., there's no pair a+b=1 and a+b+c=2, so that the shorter equation could be subtracted from the longer equation)
        for s in range(1, 8+1):                                                         # 's' means short. # Why up to 8? Because a single '1' cell, resulting from a forced guess, can have 8 neighbours; some of these neighbours can be shared with other cells in case of a compulsory guess having been made (the lonely '1' in the middle would be the guess then, obviously).
            short_equations = self.numberOfVariables_to_equations[s]                    # gets all equations with 's' number of variables, 'shorty_vars' below
            for shorty in short_equations:
                shorty_vars, shorty_sum = shorty                                        # e.g. if the equation was a+b+c=1, then shorty_vars = (a,b,c) and shorty_sum = 1)
                for l in range (s+1, 8+1):                                              # l for the length of a possibly existing longer-than-shorty equation
                    longer_equations = self.numberOfVariables_to_equations[l]           # 0 or more long_equations
                    for longy in longer_equations:
                        all_shorty_vars_found_in_this_longer_equation = True            # what this is for: if we have a+b+c = 1 (shorty) and a+b+c+d=1 (longy; it has more variables than 'shorty'), we get d=0 by subtracting shorty from longy. Or if shorty is 'a+b=1' and longy is 'a+b+c+d+e=2', then after subtraction we have c+d+e=1. That's why I'm checking if EVERY SINGLE variable in shorty is found in longy, before subtracting and registering the result as a potentially new equation (possibly solving a variable, OR helping later on with other equations). In the case of minesweeper, there should not be any case NEEDED where one has to do a subtraction where you end up with some terms negative; hence the check is justified.
                        longy_vars, longy_sum = longy
                        for variable in shorty_vars:
                            if variable not in longy_vars:
                                all_shorty_vars_found_in_this_longer_equation = False
                                break
                        if all_shorty_vars_found_in_this_longer_equation:               # if shorty is a+b=1, and longy is a+b+c=2, then as a and b both were found in longy, we go here and perform the subtraction
                            # SUBTRACTION IS DONE HERE; subtract the shorter equation from the longer one, if all shorty vars were found in the longer equation, as is hopefully obvious from the check 'all_shorty_vars_found_in_this_longer_equation == True' above
                            result_equation = (tuple(var for var in longy_vars if var not in shorty_vars), longy_sum - shorty_sum) # since factors for all variables are 1, for all variables that were found in both shorty and longy, they are subtracted to 0. As for the sum, it's the longy_sum - shorty_sum
                            equations_to_check_for_found_solutions.append(result_equation)
        found_solutions, subtractions_done = self.find_solutions_from_equations(equations_to_check_for_found_solutions)
        self.modify_iterables_after_iterations_in_factor_one()                          # this is for modifying all those variables that are part of 'self.numberOfVariables_to_equations' or other targets of iteration loops above, and which thus could not be removed during iterations above without causing an error
        if not subtractions_done:                                                       # possible cases: (1) all equations were of equal length , (2) they don't share common variables -> can't be solved without guessing
            found_new_variables = self.find_solutions_from_equations(self.unique_equations)
            if not found_new_variables:
                pass # forced guess. TO-DO; handle this here and/or in 'botGame.py'. Possibly will be implemented in 'botGame.py', because 'CSP_solver.py' doesn't (currently at least) have information about unclicked cell locations
        if how_many_rounds > 1:
            self.factor_one_binary_solve(how_many_rounds-1)

    def find_solutions_from_equations(self, equations:list) -> bool:                    # this checks if (1) a+b+...=0 -> then a,b,... = 0, since every variable is 0 or 1, (2) if the length of the variables is 1, then there's only one variable x with value y -> mark variable x as y, (3) if a new equation is found, then check it and mark all variables associated with it
        new_solutions = []
        equations_to_add = []
        found_solutions = False
        subtractions_done = False
        for variables, summa in equations:
            if summa == 0:
                found_solutions = True
                for var in variables:
                    new_solutions.append((var, 0))
            elif len(variables) == 1:
                new_solutions.append((variables[0], summa))
                found_solutions = True
            else:
                if (variables, summa) not in self.unique_equations:                     # if the equation is longer than 1 (e.g. if 'its a+b=1) and not =0 (not a+b=0), and if it's not already in 'self.unique_equations', then add it to 'self.unique_equations'
                    equations_to_add.append((-1, -1, variables, summa))                 # why (-1, -1) is included in front (it's (x,y)): because 'add_equations_if_new()' will feed the equations to 'update_equations' which takes this format. Also, this (-1,-1) means that it's not an original equation originating from a single cell on the map; it means that this equation is the result of a calculation (no matter how simple the calculation is)
                    subtractions_done = True
        for new_solution in new_solutions:
            self.mark_var_as_solved_and_update_related_info(new_solution)
        self.add_equations_if_new(equations_to_add)                                     # these were gathered in a list, because 'self.numberOfVariables_to_equations' can't be changed during its iteration
        return found_solutions, subtractions_done
    
    def mark_var_as_solved_and_update_related_info(self, new_solution:tuple) -> None:
        solved_var, summa = new_solution
        self.solved_variables.add((solved_var, summa))
        if solved_var in self.variable_to_equations:
            equations_with_the_var = self.variable_to_equations[solved_var]
            for variables, value in equations_with_the_var:
                self.update_equation((-1,-1, (variables), value))                       # this updates all equations with the newly solved variable, for example if a=1 was solved, then for a+b+e=2 -> b+e=1, etc.
            self.variable_to_equations[solved_var] = set()                              # now that all info regarding this solved variable and the equations containing this solved variable has been updated, I can empty the set of equations containing this variable (i.e., they no longer should contain this variable, as its value has been set as 0 or 1 in those equations)

def format_equation_for_csp_solver(x:int, y:int, variables:tuple, surrounding_mine_count:int) -> list:
    # NB! 'variables' has to be a tuple OR something that can be converted to a tuple; so 
    variables = tuple(coordinate_tuple for coordinate_tuple in variables)  # if there's a cell with (x,y) = (4,5) in self.front, then the variable name shall be '(4,5)'. Simple and effective. The constraint for each variable is [0,1], meaning that the solution for each variable has to be 0 or 1.
    input_addition = [x, y, variables, surrounding_mine_count]
    return input_addition

if __name__ == '__main__':
    
    def print_solved_variables(csp:CSP_solver) -> None:
        if len(csp.solved_variables) > 1:
            for variable, value in sorted(csp.solved_variables):
                print("- solved a new variable!", variable , "=", value)
        else:
            print("- solved a new variable!", csp.solved_variables[0] , "=", csp.solved_variables[1])


    '''                                             answer (which is printed also): 
    Example: solving                                a = 0
    a + b = 1                                       b = 1
    a + c + d = 1                                   c = 1
    c + d + e = 2                                   d = 0
    d + e = 1                                       e = 1                                       
    
    The only possible answer for this group of 4 equations, when a,b,c,d,e ∈ {0,1}, is obtained in 3 parts: (1) c = 1 based on 3rd and 4th equations, then (2) -> a+d=0 so a=0 and d=0 (CSP), (3) -> b=1 and e=1. Part (2) could be said to be 'CSP' (constraint satisfaction problem) where the constraint is simply the fact that every variable is either 0 or 1.
    '''                                                     # note that coordinates (x,y) do not matter regarding the solving itself; they are for bookkeeping - it's easier to visualize and check things when the coordinates are maintained
    eq1 = [0, 1, ('a', 'b'), 1]                             # (x,y) = (0,1), equation is 'a + b = 1' (the first one above in orange!)
    eq2 = [1, 1, ('a', 'c', 'd'), 1]
    eq3 = [2, 1, ('c', 'd', 'e'), 2]
    eq4 = [3, 1, ('d', 'e'), 1]
    csp = CSP_solver()
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
    csp.factor_one_binary_solve()                           # PRINT: see answer above in orange
    print_solved_variables(csp)

    '''from the above, as c=1 is solved, we get:'''

    ''' 
    From the above, after c=1, we get
    a + b = 1
    a + d = 0
    d + e = 1
    d + e = 1
    TO-DO: it only gets a = 0, d = 0, but nothing after that. Fix the check commencing so that also the others are added to 'self.solved_variables' right away.
    '''
    eq1 = [0, 1, ('a', 'b'), 1]
    eq2 = [1, 1, ('a', 'd'), 0]
    eq3 = [2, 1, ('d', 'e'), 1]
    eq4 = [3, 1, ('d', 'e'), 1]
    csp = CSP_solver()
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
    csp.factor_one_binary_solve()                          # PRINT: "solved a new variable! Variable: c = 1" which is correct
    print_solved_variables(csp)
    
    ###### a minesweeper map, where X means 'unclicked' cell, * is a 'mine' cell (not seen by the player), and 1 is '1' cell, 2 is '2' cell. Every # is edge of the map, essentially means nothing
    #X*X*#
    #1121#
    ######
    
    # the above map is described by these inputs that are used as input for 'add_equations'
    c01 = [0, 1, ((0,0), (0,1)), 1]             # 'c01' means 'cell x=0 y=1'. There are 2 variables in C01, '(0,0)' and '(0,1)', and the sum of these two is 1. The variable names mean (x,y), and each variable is either 0 or 1, meaning the number of mines in that cell (x,y) of the minesweeper map.
    c11 = [1, 1, ((0,0), (1,0), (2,0)), 1]
    c21 = [2, 1, ((1,0), (2,0), (3,0)), 2]
    c31 = [3, 1, ((2,0), (3,0)), 1]
    csp = CSP_solver()
    csp.add_equations_if_new([c01, c11, c21, c31])
    csp.factor_one_binary_solve()                          # PRINT: "solved a new variable! Variable: (1,0) = 1" which is correct! It means that (x,y) = (1,0) is a mine, which it indeed is.

    print_solved_variables(csp)


'''
This class is exclusively for MinesweeperBot's botGame; hence, all equations are 1st order, and of the type 

    q*a + w*b + e*c +... = k

where all factors and variables ∈ N (NB: the original 'raw' equations fed into the 'CSP_solver' will never evaluate to less than 1; there would be nothing to solve in those kinds of equations, as the automatic answer would be 0 for all terms, as each term has to be 0 or 1)

In fact, all raw equations that come straight from the minesweeper map have factors (q,w,e above) = 1, because there is one of each neighbour for each cell.

All the operations I need for handling these equations are (1) subtraction between these linear equations and (2) the inspection of constraint that each cell ∈ {0,1}. This is done by checking if for example ...+2x+... = 1, where the only possible solution for x is x=0, since if x was 1, others would have to be negative, or if a+b+c+... = 0, which means that all terms are 0. This latter one (all 0) can happen only after initial processing, as (like mentioned above), no such equations come 'raw' from the map.
'''

'''What is done:
- sort equations by length. Start with the shortest one, and see which of the longer equations has all its terms -> subtract -> see if the new equation is unique. Efficient
- save all solved variables
'''