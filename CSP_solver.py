'''to-do:
- why is the last test flaky? most probable reason; iteration through sets varies in order, and through this, sometimes all variables are solved (yep) and sometimes NONE (YEP - I know! Amazing, right?)
- in 'factor_one_solve', an easy way to check if subtracting the subset from the larger set is correct is as follows: if you end up with a+b+.... < 0, the subtraction was WRONG - something was wrong in the code itself. Why; because x ∈{0,1} for all cells x, and because I'm always subtracting a subset from a larger or equally sized set. Therefore, as every element of each set is 0 or 1, it is not possible to end up with a negative result for the resulting equation. For example: a+b+c = 1, a+b+c+d = 2 -> d = 1. The resulting equation can never have a negative value, if every element of the subset is found in the larger set, and every element x ∈{0,1} for all cells x. Therefore, it would be good the specifically add this at some point to facilitate debugging.
'''
from itertools import combinations

# NB! 'sum' = the label of the cell in minesweeer map (the number seen on the cell)
# Searching: (1) 'variable_to_equations'; get all equations that contain a specific 'variable' as key, (2) self.json: get all the info about an equation; {equation : info_structures_here}. Together, these two enable efficient search of info about any equation based on the variable included in the equation
class CSP_solver:
    def __init__(self):

        self.unique_equations = set()                               # { ((var1, var2, ..), sum_of_mines_in_vars), (...) }. Each var (variable) has format (x,y) of that cell's location; cell with a number label 1...8 = var. Here, I want uniqe EQUATIONS, not unique LOCATIONS, and therefore origin-(x,y) is not stored here. It's possible to get the same equation for example from two different sides, and via multiple different calculation routes, and it's of course possible to mistakenly try to add the same equation multiple times; that's another reason to use a set() here, the main reason being fast search from this hashed set.        
        self.solved_variables = set()                               # ((x,y), value); the name of the variable is (x,y) where x and y are its location in the minesweeper map (if applicable), and the value of the variable is either 0 or 1, if everything is ok (each variable is one cell in the minesweeper map, and its value is the number of mines in the cell; 0 or 1, that is)
        self.impossible_mine_combos = set()
        self.possible_mine_combo_groups = set()
        
        self.variable_to_equations = dict()                         # { variable_a : set(equation5, equation12, equation4,...), variable_b : set(equation3, equation4...)}. The format of 'equation' is ((variable1, variable2,...), sum_of_the_variables)
        self.numberOfVariables_to_equations = {                     # { numberOfVariables : set(equation1, equation2, ...) }; each key of this dict is integer x, and x's values are all equations with x number of variables. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables; if all the variables in the shorter equation are found in the longer equation, then perform subtraction to get rid of those varibles in the longer equation (linear equation solving), then save the formed result equation to 'self.unique_equations' and 'self.numberOfVariables_to_equations'.
            x:set() for x in range(0, 8+1)                          # Why up to 8? Because a single '1' cell, resulting from a forced guess in the middle of unclicked cells, has 8 neighbours, hence 8 variables in the equation for that '1' cell; some of these neighbours can be shared with other cells in case of a compulsory guess having been made (the lonely '1' in the middle would be the guess then, obviously). NB! It's possible that when all variables in a given equation have just been solved, all are canceled out, and at that point the length of the equation (i.e. the number of variables) becomes 0; that's why I'm starting from 0.
        }                                                           # { numberOfVariables : set(equation1, equation2, ...) }; all equations with numberOfVariables = x. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables.
        self.var_to_equations_updated_equations_to_add = set()      # during iteration of these, these cannot be directly changed -> gather a list, modify after iteration is over
        self.var_to_equations_obsolete_equations_to_remove = set()  # same as above comment

    # 100% solution: try all combinations of ones (=mines), and see if it satisfies all equations where that variable is. From all of these combinations that DO satisfy all the equations, find columns where a variable is always 0 or 1 -> it HAS to be 0 or 1.
    def absolut_brut(self, rounds=1):
        all_possible_combinations_of_mines = set()
        for variables, summa in self.unique_equations:
            mine_location_combinations = combinations(variables, summa)         # all possible combinations of mines for this equation
            this_eq_group = []                                                  # NB! All the possible solutions for THIS equation ('variables', 'summa' constitutes an equation in 'self.unique_equations') are gathered here; in the end, I have to solve each of these 'individual' equations, AND find a solution that satisfies all the other equations as well.
            for mine_location_combination in mine_location_combinations:
                combo = []                                                      # for all vars a,b,c,... {a:1, b:0, c:0, ....}
                for var in variables:
                    if var in mine_location_combination:
                        combo.append((var, 1))                                  # it's entirely possible to just add the 1s, if the definition is that all others are 0
                    else:
                        combo.append((var, 0))
                combo = tuple(combo)

                if combo not in self.impossible_mine_combos:
                    this_eq_group.append(combo)
                    all_possible_combinations_of_mines.add(combo)
                    
            self.possible_mine_combo_groups.add(tuple(this_eq_group))
        pass

    def inter(self):
        all_vars = set(self.variable_to_equations.keys())
        for variables, summa in self.possible_mine_combo_groups:
            pass

                


        

        

    # NB! This is called, when adding new equations for the first time, AND after finding new variables IF the related equations are (1) new and (2) do not become single solved variables as well (i.e. if the related equations are not reduced from equations like a+b=1 to just solved single variables like b=1). Hence, sometimes the 'self.update_equation(equation)' is necessary.
    def add_equations_if_new(self, equations:list) -> None:                             # equations = [(x, y, ((x1, y1), (x2, y2), ...), summa), ...]; so each equation is a tuple of of x, y, unflagged unclicked neighbours (coordinates; unique variables, that is!), and the label of the cell (1,2,...8)
        for equation in equations:                                                      # (x,y,(variables),sum_of_variables)
            x, y, variables, summa = self.update_equation_and_related_info(equation)    # both updates, IF NECESSARY, 'self.unique_equations' (removes the old one, adds the shorter one), AND returns the new one here right away. NB: this small sidetrack is very short in cases where an equation is truly added for the first time (such as in 'botGame.py' from where this 'CSP_solver' class is used)
            if (variables, summa) not in self.unique_equations:                         # TO-DO; why are the old equations, with already-solved variables, still in self.variable_to_equations? can't hash sets; 'variables' has to be a tuple!
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

    # this is used in (1) 'self.add_equations_if_new()' and in (2) 'self.factor_one_solve()' (3) 'self.update_info_after_solving_new_variable'; (1) purpose: do not add 'new' equations that have been already (partially) solved; that is, take into account the fact that some variables have been solved already (2) TO-DO writestuffhere
    # (1) in all equations where solved variables exist, reduce for solved variables (2) update the reduced form to 'self.unique_equations' (3) update to 'self.numberOfVariables_to_equations' (4) others? TO-DO, CHECK!
    def update_equation_and_related_info(self, equation:tuple) -> None:                                      # equation = ( (var1, var2, ...), sum_of_variables). There's no origin (x,y) here, because all of those are unique, and irrelevant here!
        x, y, original_vars, original_summa = equation
        unsolved_variables, sum_of_solved_vars, solved_variables = self.filter_out_solved_variables(original_vars)
        if len(unsolved_variables) != len(original_vars):                                   # if one or more variables in 'original_vars' had indeed been solved already; in that case we need to update all related information: (1) 'self.unique_equations', (2) 'self.numberOfVariables_to_equations', (3) 'self.variable_to_equations'. Otherwise 'factor_one_solve' will have old info and will not work.
            if (original_vars, original_summa) in self.unique_equations:
                self.unique_equations.remove((original_vars, original_summa))
            # Remove the old equation from self.numberOfVariables_to_equations; the new one is either (1) a shorter equation, or (2) a (bunch of) new solved variable(s), which will be sorted out further below
            if len(original_vars) in self.numberOfVariables_to_equations:
                if (original_vars, original_summa) in self.numberOfVariables_to_equations[len(original_vars)]:
                    self.numberOfVariables_to_equations[len(original_vars)].remove((original_vars, original_summa))

            # TO-DO: check if this updating self.variable_to_equations works as intended! This is quite an arduous process. However, it's not very unefficient thanks to sets, and due to the limited length of vars per equation (usually 2-5 per equation, max is 8)
            for solved_var, solved_value in solved_variables:
                immediate_equations = self.variable_to_equations[solved_var]    # NB! This alone is not enough; we need to check the need for updating for all the equations for all the variables in all the equations. Yeah, can be dozens of them in total - but not too bad in reality! Also, this is done only when needed, and the below checks ensure that only ACTUAL equations are updated, not the ones summing up to 0, or where the number of variables equals to the sum.
                for vars, value in immediate_equations:
                    for var in vars:
                        if var != solved_var:                                       # if the 'solved_var' is 'c', then we don't want to handle 'c' case here, otherwise the result would only have other variables. Instead, 'self.variable_to_equations[solved_var].clear()' as the very last thing below.
                            old_equations = self.variable_to_equations[var]
                            for old_vars, old_value in old_equations:
                                if solved_var in old_vars:
                                    updated_value = old_value - solved_value
                                    if updated_value != 0:                          # if the updated_value == 0, then it's not an equation anymore, it's a solved variable, which has been saved in self.solved_variables already.
                                        if updated_value != len(old_vars)-1:        # we know already that 'solved_var' is in 'old_vars' (because of the if clause above checked it to be the case already). Then, if the number of the remaining variables (-1) equals to the updated value, they all have to be one -> that shouldn't be in the 'self.variable_to_equations' either, as that too is a solved case where all the variables are 1, and this is handled elsewhere (no need to add an equation here). I know this is complicated!
                                            updated_variables = tuple(var for var in old_vars if var != solved_var)
                                            self.var_to_equations_updated_equations_to_add.add((var, updated_variables, updated_value))
                                    self.var_to_equations_obsolete_equations_to_remove.add((var, old_vars, old_value))
                
            if original_summa-sum_of_solved_vars == 0:                          # old equation sum - (minus) the new, updated equation sum. If this is zero, then all the remaining variables are 0!
                for var in unsolved_variables:
                    self.solved_variables.add((var,0))
                    # self.mark_var_as_solved_and_update_related_info((var,0))  # set changed size during iteration; because, that function is calling this function, and in that function 'self.variable_to_equations' is directly changed...?
            if len(unsolved_variables) == 1:                                    # NB! NOT 'elif'!
                self.solved_variables.add((unsolved_variables[0], original_summa-sum_of_solved_vars))
                # self.mark_var_as_solved_and_update_related_info((unsolved_variables[0], original_summa-sum_of_solved_vars))
            elif len(unsolved_variables) == original_summa-sum_of_solved_vars:
                for var in unsolved_variables:
                    self.solved_variables.add((var,1))
                    # self.mark_var_as_solved_and_update_related_info((var,1))
            
            # NB! This should NOT BE in any 'if' clauses!! I had made that blunder at one point, leading to missing 'self.unique_equations' which led to major deficiencies in solving capability in some cases.
            self.unique_equations.add((unsolved_variables, original_summa-sum_of_solved_vars))  # why 'else': we don't need 'equations' that are ({c},1) or such; these are saved to 'self.solved_variables'. So let's keep equations as actual equations.
            if (unsolved_variables, original_summa-sum_of_solved_vars) not in self.numberOfVariables_to_equations[len(unsolved_variables)]:      # technically this is a redundant check, since we're adding to a set, but the check is useful for showing the logic AND useful for debugging
                self.numberOfVariables_to_equations[len(unsolved_variables)].add((unsolved_variables, original_summa-sum_of_solved_vars))
            x = y = -1                                                                          # if information from already solved variables has been used to simplify equation, then this equation no longer has defnitivie single (x,y) origin from the minesweeper map; hence, mark it as (-1,-1).
        return [x, y, unsolved_variables, original_summa-sum_of_solved_vars]

    def filter_out_solved_variables(self, variables) -> tuple:                          # returns ((unsolved_variables), sum_of_solved_variables); this is for comparison before-and-after in 'update_equation()', where from this function is called. If something changed, then update it further in 'update_equation()'
        unsolved_vars = []
        solved_vars = []
        sum_of_solved_vars = 0
        for var in variables:
            # ((x,y), value). I can't know if it's 0 or 1, so I'm checking both. 'var' = (x,y) and each var is unique cell of the minesweeper map
            if (var, 0) in self.solved_variables:
                solved_vars.append((var,0))
            elif (var, 1) in self.solved_variables:
                solved_vars.append((var,1))
                sum_of_solved_vars += 1
            else:  # ((x,y), value), in 'self.solved_variables'
                unsolved_vars.append(var)
        return tuple(unsolved_vars), sum_of_solved_vars, solved_vars                    # you can't hash sets or lists (not immutable), hence a tuple is returned instead for 'unsolved_vars'. Hashing of 'unsolved_variables' is needed in 'add_equations' from where this function is used.

    def find_solutions_from_single_equations(self, equations:list) -> bool:             # this checks if (1) a+b+...=0 -> then a,b,... = 0, since every variable is 0 or 1, (2) if the length of the variables is 1, then there's only one variable x with value y -> mark variable x as y, (3) if a new equation is found, then check it and mark all variables associated with it
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
            elif len(variables) == summa:
                found_solutions = True
                for var in variables:
                    new_solutions.append((var, 1))
            else:
                if (variables, summa) not in self.unique_equations:                     # if the equation is longer than 1 (e.g. if 'its a+b=1) and not =0 (not a+b=0), and if it's not already in 'self.unique_equations', then add it to 'self.unique_equations'
                    equations_to_add.append((-1, -1, variables, summa))                 # (1) if the equation wasn't c=1 or a+b+c=3 or a+b+c+d+...=0, then add this to the set of equations (2) why (-1, -1) is included in front (it's (x,y)): because 'add_equations_if_new()' will feed the equations to 'update_equations' which takes this format. Also, this (-1,-1) means that it's not an original equation originating from a single cell on the map; it means that this equation is the result of a calculation (no matter how simple the calculation is)
                    subtractions_done = True
        for new_solution in new_solutions:                                              # immediately add ALL the newly solved variables; only THEN (belo) update the related info; avoiding unnecessary computation regarding the related info!
            self.solved_variables.add(new_solution)
        for new_solution in new_solutions:
            self.update_related_info_for_solved_var(new_solution)
        self.add_equations_if_new(equations_to_add)                                     # these were gathered in a list, because 'self.numberOfVariables_to_equations' can't be changed during its iteration
        return found_solutions, subtractions_done
    
    def update_related_info_for_solved_var(self, new_solution:tuple) -> None:
        solved_var, value = new_solution
        
        # why am I not performing this commented-out line below here? BECAUSE: if there are multiple solved vars, this creates multiple times the work (unnecessary computation)! In English: ALL the newly solved variables should be added to 'self.solved_variables' first, THEN update the info regarding those solved variables, so that partially obsolete equations are not created in the process! For example; imagine a loop that solves 3 variables. If I start updating all the info regarding ONE solved variable, I have to do that 3 times, compared to if I mark all 3 as solved, THEN update all related info ONE time c:
        # self.solved_variables.add((solved_var, value))                                # 'self.solved_variables' is the set of tuples that is utilized in 'botGame.py'! So this is the solution carrier info structure that's used by botGame.py, so to say.
        if solved_var in self.variable_to_equations:                                    # then update all those equations, then clear the now-obsolete list of equations mapped for this variable
            equations_with_the_var = self.variable_to_equations[solved_var]             # all of these have to be updated!
            for variables, value in equations_with_the_var:
                self.update_equation_and_related_info((-1,-1, (variables), value))      # NB! (1) This also adds to 'self.var_to_equations_updated_equations_to_add' and 'self.var_to_equations_updated_equations_to_remove'; hence, only AFTER completion of this loop, can I actually remove and/or add to 'self.variable_to_equations'. (2) This updates all equations with the newly solved variable, for example if a=1 was solved, then for a+b+e=2 -> b+e=1, etc.
                #self.variable_to_equations[solved_var].remove((variables, value))      # set changed size during iteration if you uncomment this
            
            # NB! the loop above HAS TO come before this one; here I'm adding new updated versions of 'self.variable_to_equations' and removing all the obsolete versions of them
            for var, old_vars, old_value in self.var_to_equations_obsolete_equations_to_remove:
                if (var, old_vars, old_value) in self.var_to_equations_updated_equations_to_add:
                    self.var_to_equations_updated_equations_to_add.remove((var,old_vars,old_value)) # this has to be checked; there's no way to know if some of these have already become obsolete during the loops
            for var, updated_vars, updated_value in self.var_to_equations_updated_equations_to_add:
                if (updated_vars, updated_value) not in self.variable_to_equations[var]:    # to show the logic and to facilitate debugging. Technically, this is not needed (for adding to set; not needed, technically speaking)
                    self.variable_to_equations[var].add((updated_vars, updated_value))
            self.var_to_equations_updated_equations_to_add.clear()                          # clear for the next round of 'self.factor_one_binary-solve()'
            for var, old_vars, old_value in self.var_to_equations_obsolete_equations_to_remove:
                if (old_vars, old_value) in self.variable_to_equations[var]:                 # needed. Sometimes, this would cause 'key_error' without checking.
                    self.variable_to_equations[var].remove((old_vars, old_value))
            self.var_to_equations_obsolete_equations_to_remove.clear()                  # clear for the next round of 'self.factor_one_binary-solve()'
            self.variable_to_equations[solved_var] = set()                              # ONLY clearing for the solved var is not enough, that's why above, every set of obsolete equations (i.e. containing variables that have been solved, now in 'self.solved_variables') that was marked for removal is removed, while the corresponding updated equations are added above. I did the updating in 'self.update_equation_and_related_info', because that's where we're calculating the updated value for the partially solved equations already anyways, having the necessary updating information available. So, in short: I should update for new, already-solved variables, not ONLY clear the whole thing does this occur prematurily??? Anyways: now that all info regarding this solved variable and the equations containing this solved variable has been updated above, I can empty the set of equations containing this variable (i.e., they no longer should contain this variable, as its value has been set as 0 or 1 in those equations)

def format_equation_for_csp_solver(x:int, y:int, variables:tuple, surrounding_mine_count:int) -> list:
    # NB! 'variables' has to be a tuple OR something that can be converted to a tuple
    variables = tuple(variables)  # if there's a cell with (x,y) = (4,5) in self.front, then the variable name shall be '(4,5)'. Simple and effective. The constraint for each variable is [0,1], meaning that the solution for each variable has to be 0 or 1.
    input_addition = [x, y, variables, surrounding_mine_count]
    return input_addition


#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

if __name__ == '__main__':
    def print_solved_variables(csp:CSP_solver, name='random test', expected_result='') -> None:
        print(f'\nSolving "{name}"')
        concat = ''
        if len(csp.solved_variables) >= 1:
            for variable, value in sorted(csp.solved_variables):
                print("- solved a new variable!", variable , "=", value)
                concat += str(value)
        elif len(csp.solved_variables) == 0:
            print('- NO SOLVED VARIABLES!')
        if concat == expected_result:
            print('test passed!')
        else:
            print('TEST FAILED')


    ################################# Test 1a (using letters instead of (x,y) format for variables) ##########################################

    '''                                             answer: 
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
    csp.absolut_brut()       # TO-DO; fails sometimes, even if 2 ... 10 rounds! (why sometimes; because sets can be handled in undeterministic order relative to each other)     # PRINT: see answer above in orange
    print_solved_variables(csp, 'test 1a: letters. a0, b1, c1, d0, e1 expected:', '01101')

    ############################ Test 1b: same as 1a, but using (x,y) format for variables instead of letters ############################################
    
    ###### a minesweeper map, where X means 'unclicked' cell, * is a 'mine' cell (not seen by the player), and 1 is '1' cell, 2 is '2' cell. Every # is edge of the map, essentially means nothing
    #X*X*#
    #1121#
    ######
    
    # the above map is described by these inputs that are used as input for 'add_equations'
    eq1 = [0, 1, ((0,0), (0,1)), 1]
    eq2 = [1, 1, ((0,0), (1,0), (2,0)), 1]
    eq3 = [2, 1, ((1,0), (2,0), (3,0)), 2]
    eq4 = [3, 1, ((2,0), (3,0)), 1]
    csp = CSP_solver()
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
    csp.absolut_brut()

    print_solved_variables(csp, 'test 1b: (x,y): (0,0)=0, (0,1)=1, (1,0)=1, (2,0)=0, (3,0)=1 expected:', '01101')

    '''correct result:
    - solved a new variable! (0, 0) = 0
    - solved a new variable! (0, 1) = 1
    - solved a new variable! (1, 0) = 1
    - solved a new variable! (2, 0) = 0
    - solved a new variable! (3, 0) = 1'''

    ########################## Test 1c: will it finish a partially solved equation, starting with equation format? #############################################

    '''from the above, as c=1 is solved, we get:'''

    ''' 
    From the above, after c=1, we get
    a + b = 1
    a + d = 0
    d + e = 1
    d + e = 1
    expected: a=0, b=1, d=0, e=1
    '''
    eq1 = [0, 1, ('a', 'b'), 1]
    eq2 = [1, 1, ('a', 'd'), 0]
    eq3 = [2, 1, ('d', 'e'), 1]
    eq4 = [3, 1, ('d', 'e'), 1]
    csp = CSP_solver()
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
    csp.absolut_brut()                          
    print_solved_variables(csp, 'test 1c: letters. 0101 expected', '0101')

    ############################## Test 2 #############################################
    '''                                             answer (which is printed also): 
    Example: solving                                a = 0
    a + b + d = 2                                   b = 1
    a + b + c + d + e = 2                           c = 0
    b + c + e = 1                                   d = 1
    d + e = 1                                       e = 0                                       
    
    The only possible answer for this group of 4 equations, when a,b,c,d,e ∈ {0,1}, is obtained in 3 parts: (1) c = 1 based on 3rd and 4th equations, then (2) -> a+d=0 so a=0 and d=0 (CSP), (3) -> b=1 and e=1. Part (2) could be said to be 'CSP' (constraint satisfaction problem) where the constraint is simply the fact that every variable is either 0 or 1.
    '''                                                   

    eq1 = [0, 1, ('a', 'b', 'd'), 2]
    eq2 = [1, 1, ('a', 'b', 'c', 'd', 'e'), 2]
    eq3 = [2, 1, ('b', 'c', 'e'), 1]
    eq4 = [1, 2, ('d', 'e'), 1]
    csp = CSP_solver()
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
    csp.absolut_brut()                          
    print_solved_variables(csp, 'test 2, letters. 01010 expected:', '01010')

    

    ############################ Test 3a: letters ############################################
    
    ###### a minesweeper map, where X means 'unclicked' cell, * is a 'mine' cell (not seen by the player), and 1 is a '1' cell, 3 is a '3' cell. Every # is edge of the map, essentially means nothing
    #001*#
    #113X#
    #X*X*#
    ######

    # the above map is described by these inputs that are used as input for 'add_equations'
    eq1 = [0, 1, ('a', 'b'), 1]
    eq2 = [1, 1, ('a', 'b', 'c'), 1]
    eq3 = [2, 0, ('d', 'e'), 1]
    eq4 = [2, 1, ('d', 'e', 'f', 'b'), 3]
    csp = CSP_solver()
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
    csp.absolut_brut()

    print_solved_variables(csp, 'test 3a, letters. 0101 expected', '0101')

    '''correct result: a,c,e=0; b,f,d = 1. This requires the constraints that each is 0 or 1
    '''

    ############################ Test 3b: (x,y) ############################################

    ###### a minesweeper map, where X means 'unclicked' cell, * is a 'mine' cell (not seen by the player), and 1 is a '1' cell, 3 is a '3' cell. Every # is edge of the map, essentially means nothing
    #001*#
    #113X#
    #X*X*#
    ######

    # the above map is described by these inputs that are used as input for 'add_equations'
    c01 = [0, 1, ((0,2), (1,2)), 1]                         # 'c01' means 'cell x=0 y=1'. There are 2 variables in C01, '(0,0)' and '(0,1)', and the sum of these two is 1. The variable names mean (x,y), and each variable is either 0 or 1, meaning the number of mines in that cell (x,y) of the minesweeper map.
    c11 = [1, 1, ((0,2), (1,2), (2,2)), 1]
    c20 = [2, 0, ((3,0), (3,1)), 1]
    c21 = [2, 1, ((3,0), (3,1), (3,2), (1,2)), 3]
    csp = CSP_solver()
    csp.add_equations_if_new([c01, c11, c20, c21])
    csp.absolut_brut()

    print_solved_variables(csp, 'test 3b, (x,y). 0101 expected', '0101')

    ############################ Test 4a: letters ############################################
    
    eqi     = [3, 1, ('b', 'c'), 1]                         
    eqiii   = [3, 3, ('a', 'b', 'c', 'd', 'e'), 2]
    eqv     = [2, 4, ('a', 'f'), 1]
    eqvi    = [3, 4, ('a', 'd', 'e', 'f', 'g'), 2]
    eqa     = [2, 7, ('h', 'i'), 1]
    eqb     = [3, 5, ('e', 'f', 'g', 'h', 'i'), 2]
    csp = CSP_solver()
    csp.add_equations_if_new([eqi, eqiii, eqv, eqvi, eqa, eqb])
    csp.absolut_brut(3)                                  # NB! after 3 rounds minimum, e=0 is solved! A smaller number of rounds is not enough. This is ok and expected given the functions written in the class, as not everything is recursively updated until the end of the world (as this would complicate things even more!); also, nb! The purpose is not to be able to solve everything in one go, as that would also mean that pressing 'b' once in 'botGame.py' would proceed a huge number of steps at a time, AND this has nothing to do, as such, with efficiency either; so I want to divide this into small(ish) steps whenever possible, facilitating visualization and debugging that way, as there's no real reason not to do this. In fact, efficiency-wise, it's better to run as little as CSP_solver as possible, instead relying on the much simpler 'simple_solver' in 'botGame.py' as possible

    print_solved_variables(csp, 'test 4a, letters. 0 expected', '0')

    ########################## Test 5a: letters. Based on 'Esim_expert_1.png', which wasn't solved by pressing 'b' (i.e., this test is for actual debugging) #
    
    eq1     = [-1, -1, ('a', 'b'), 1]                         
    eq2     = [-1, -1, ('a', 'b', 'c', 'd', 'e'), 2]
    eq3     = [-1, -1, ('d', 'e', 'f'), 2]
    eq4     = [-1, -1, ('e', 'f', 'g'), 2]
    eq5     = [-1, -1, ('f', 'g', 'h', 'i', 'j'), 1]
    
    csp = CSP_solver()
    csp.add_equations_if_new([eq1, eq2, eq3, eq4, eq5])
    csp.absolut_brut(2)                                  # NB! This needs 2 rounds!
    # TO-DO: Thanks to this, I added more CSP conditions -> now it's sometimes ENTIRELY solved, sometimes NOT AT ALL (0 variables solved!)

    print_solved_variables(csp, 'test 5a, letters. c0, d0, e1, f1, g0, h0, i0, j0 expected', '00110000') # expected: cdefg 00110


'''
This class is exclusively for MinesweeperBot's botGame; hence, all equations are 1st order, and of the type 

    q*a + w*b + e*c +... = k

where all factors and variables ∈ N and k ∈[0,8] (NB: the original 'raw' equations fed into the 'CSP_solver' will never evaluate to less than 1; there would be nothing to solve in those kinds of equations, as the automatic answer would be 0 for all terms, as each term has to be 0 or 1)

In fact, all raw equations that come straight from the minesweeper map have factors (q,w,e above) = 1, because there is one of each neighbour for each cell.

All the operations I need for handling these equations are (1) subtraction between these linear equations and (2) the inspection of constraint that each cell ∈ {0,1}. This is done by checking if for example ...+2x+... = 1, where the only possible solution for x is x=0, since if x was 1, others would have to be negative, or if a+b+c+... = 0, which means that all terms are 0. This latter one (all 0) can happen only after initial processing, as (like mentioned above), no such equations come 'raw' from the map.
'''

'''What is done:
- sort equations by length. Start with the shortest one, and see which of the longer equations has all its terms -> subtract -> see if the new equation is unique. Efficient
- save all solved variables
- bookkeeping of equations (this could be flaky, to-do partly still)

'''