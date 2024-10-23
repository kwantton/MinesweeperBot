'''
- NOTE WELL! This 'CSP_solver_old' is auxiliary; it WORKS for producing SOME easy answers; it's meant to produce additional answers quickly to see, if something 'easier' can be squeezed out before utilizing 'CSP_solver' (the not-old version, which has heavier machinery). So this does NOT solve all cases, but the things it solves, it solves correctly and quickly.
NB! The last test is flaky exactly because it sometimes produces ALL the answers, sometimes not; depends on the handling order (order of iterating through sets)
to-do:
- why is the last test flaky? most probable reason; iteration through sets varies in order, and through this, sometimes all variables are solved (yep) and sometimes NONE (YEP - I know! Amazing, right? Sometimes every var is solved, sometimes none c: BUT - those that ARE solved, are correct, which is good.)
- in 'factor_one_solve', an easy way to check if subtracting the subset from the larger set is correct is as follows: if you end up with a+b+.... < 0, the subtraction was WRONG - something was wrong in the code itself. Why; because x ∈{0,1} for all cells x, and because I'm always subtracting a subset from a larger or equally sized set. Therefore, as every element of each set is 0 or 1, it is not possible to end up with a negative result for the resulting equation. For example: a+b+c = 1, a+b+c+d = 2 -> d = 1. The resulting equation can never have a negative value, if every element of the subset is found in the larger set, and every element x ∈{0,1} for all cells x. Therefore, it would be good the specifically add this at some point to facilitate debugging.
'''

# NB! 'sum' = the label of the cell in minesweeer map (the number seen on the cell)
# Searching: (1) 'variable_to_equations'; get all equations that contain a specific 'variable' as key, (2) self.json: get all the info about an equation; {equation : info_structures_here}. Together, these two enable efficient search of info about any equation based on the variable included in the equation
class CSP_solver:
    def __init__(self):

        self.reset_all()

    def reset_all(self):
        self.unique_equations = set()                           # { ((var1, var2, ..), sum_of_mines_in_vars), (...) }. Each var (variable) has format (x,y) of that cell's location; cell with a number label 1...8 = var. Here, I want uniqe EQUATIONS, not unique LOCATIONS, and therefore origin-(x,y) is not stored here. It's possible to get the same equation for example from two different sides, and via multiple different calculation routes, and it's of course possible to mistakenly try to add the same equation multiple times; that's another reason to use a set() here, the main reason being fast search from this hashed set.        
        self.solved_variables = set()                           # ((x,y), value); the name of the variable is (x,y) where x and y are its location in the minesweeper map (if applicable), and the value of the variable is either 0 or 1, if everything is ok (each variable is one cell in the minesweeper map, and its value is the number of mines in the cell; 0 or 1, that is)
        self.reassigned_variables = dict()                      # { variable_a : variable_b }. This is for those ~solved cases, where b=c; so every b will no be c forever, etc.
        self.variable_to_equations = dict()                     # { variable_a : set(equation5, equation12, equation4,...), variable_b : set(equation3, equation4...)}. The format of 'equation' is ((variable1, variable2,...), sum_of_the_variables)
        self.numberOfVariables_to_equations = {                 # { numberOfVariables : set(equation1, equation2, ...) }; each key of this dict is integer x, and x's values are all equations with x number of variables. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables; if all the variables in the shorter equation are found in the longer equation, then perform subtraction to get rid of those varibles in the longer equation (linear equation solving), then save the formed result equation to 'self.unique_equations' and 'self.numberOfVariables_to_equations'.
            x:set() for x in range(0, 8+1)                      # Why up to 8? Because a single '1' cell, resulting from a forced guess in the middle of unclicked cells, has 8 neighbours, hence 8 variables in the equation for that '1' cell; some of these neighbours can be shared with other cells in case of a compulsory guess having been made (the lonely '1' in the middle would be the guess then, obviously). NB! It's possible that when all variables in a given equation have just been solved, all are canceled out, and at that point the length of the equation (i.e. the number of variables) becomes 0; that's why I'm starting from 0.
        }                                                       # { numberOfVariables : set(equation1, equation2, ...) }; all equations with numberOfVariables = x. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables.
        self.var_to_equations_updated_equations_to_add = set()     # during iteration of these, these cannot be directly changed -> gather a list, modify after iteration is over
        self.var_to_equations_obsolete_equations_to_remove = set() # same as above comment
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

    # if a+b+c = x and a+b+d = y, then subtract => c-d=x-y ∈ {-1,0,1}. If -1, then c-d=-1, so d-c=1, so d=1, c=0. If 0, then c-d=0, so c=d; if 1, then c-d=1, so c=d+1, so c=1 and d=0.
    def equal_length_solver(self):
        for s in range (2, 8+1):                                                        # this is for EQUATION lengths, from 2 to 8; in my case I'm defining an equation as something that has at least 2 different (unsolved) variables (a variable being the minecount in the surrounding 8 cells of a given cell). So, no need to start from 1; those are handled elsewhere already, this is not for those cases. Also; they should not be in 'self.numberOfVariables_to_equations' anyways c:
            equal_length_equations = list(self.numberOfVariables_to_equations[s])
            for a in range (len(equal_length_equations)):
                differing_variable_count = 0
                vars1, summa1 = equal_length_equations[a]
                for b in range (a+1, len(equal_length_equations)):
                    vars2, summa2 = equal_length_equations[b]
                    for var1 in vars1:
                        if var1 not in vars2:
                            differing_variable_count += 1
                            if differing_variable_count > 1:
                                break
                            c = var1
                    if differing_variable_count == 1:               # this was explained above this equation. c=the same as there, d=the same as there.
                        for var2 in vars2:
                            if var2 not in vars1:
                                d = var2
                                break
                        result_value = summa1-summa2
                        if result_value == -1:                      # if c-d=-1, then d-c=1, so c=0 and d=1 (since every variable is 0 or 1!)
                            self.solved_variables.add((c,0))        # why am I not just doing this in 'update_related...'? Because if there are multiple solved vars, this creates extra work!
                            self.solved_variables.add((d,1))
                            self.update_related_info_for_solved_var((c, 0))
                            self.update_related_info_for_solved_var((d, 1))
                        elif result_value == 0:                     # if c-d=0, then c=d
                            self.reassign_variable(c,d)             # reassign every c as d, and do this in all data structures. However! I have quite accurate bookkeeping, so this is not a huge task computationally; there is not a huge number of 'unnecessary' info to update, and 'self.front' (in 'botGame.py') is well-kept.
                            # c = d. This, of course, sucks a lot. I have to update aaaaaall information according to this new piece of information. TO-DO.
                        elif result_value == 1:
                            self.solved_variables.add((c,1))
                            self.solved_variables.add((d,0))
                            self.update_related_info_for_solved_var((c, 1))
                            self.update_related_info_for_solved_var((d, 0))
    
    # NB! the 'how_many_rounds=1' is arbitrary, and is illustrative for testing (why: because it has never solved more variables after multiple rounds than after just 1 round! Adding rounds doesn't affect the result.). In 'botGame.py' I am calling one 'bot_move' per one press of key 'b' by the person running the program, and a part of each of these 'bot_move's is this 'factor_one_solve()' here. Therefore, for visualization and debugging purposes, I want to make it possible to advance one small step at a time; that's why I have the 'rounds=1' set by default. Also, performance-wise, there is no obvious way to tell if performing one or multiple of these rounds in a row is faster or not (on average; this depends on so many things, including the map itself!) without considering first if the simpler logic in 'bot_move' before this 'CSP_solver' has anything more to offer before this 'CSP_solver' is performed or not; so performance-wise, it's a bit of a (micro)mystery, at least yet, whether one should let this run for a longer time or not by default.
    # TO-DO: if a+b+c = x and a+b+d = y, then subtract => c-d=x-y ∈ {-1,0,1}. If -1, then c-d=-1, so d-c=1, so d=1, c=0. If 0, then c-d=0, so c=d; if 1, then c-d=1, so c=d+1, so c=1 and d=0.
    def factor_one_binary_solve(self, how_many_rounds=1):                               # 'factor_one' here means that each variable has a factor of exactly one (or, to be exact, zero when it's not present), no more, for this solver (e.g. a+b+c=2, never a+2b+c=2 for example, since each minesweeper map cell has exactly one of each neighbour). This should be enough; there should not be a need to sum equations in my case!
        # print('factor_one_solve():')
        self.equal_length_solver()
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
 
        found_solutions, subtractions_done = self.find_solutions_from_single_equations(equations_to_check_for_found_solutions)
        
        if not subtractions_done:                                                       # possible cases: (1) all equations were of equal length , (2) they don't share common variables -> can't be solved without guessing
            found_new_variables = self.find_solutions_from_single_equations(self.unique_equations)
            if not found_new_variables:
                # at this point: no subtractions done (i.e.; no new equations), AND no new variables found
                pass # forced guess. TO-DO; handle this here and/or in 'botGame.py'. Possibly will be implemented in 'botGame.py', because 'CSP_solver.py' doesn't (currently at least) have information about unclicked cell locations
        if how_many_rounds > 1:
            self.factor_one_binary_solve(how_many_rounds-1)

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

    # TO-DO; only if needed - I have to first fix the last flaky unit test here. (1) reassign everywhere (all data structures), (2) in 'add_equations_if_new', check for incoming variables, if they have been reassigned. This should be extremely simple.
    def reassign_variable(self, old:tuple, new:tuple) -> None:                          # when using characters instead of (x,y), this is not actually a tuple, but a string (single character)
        pass
        # if self.variable_to_equations[old]:                                             # if instead this is just {} (empty set), then don't go through every self.unique_equations, etc etc..
        #     for vars, summa in self.variable_to_equations[old]:                         # (var1, var2, ...), summa
        #         count_of_each_var = {}                                                  # for example: in case a+b+f+g, if 'old'=g and 'new'=a, then 'a+b+f+g' becomes 'a+b+f+a' = '2a+b+f'; for this, I need the COUNT of each variable!
        #         for var in vars:
        #             if var == old:
        #                 var = new
        #             if var not in count_of_each_var:
        #                 count_of_each_var[var] = 0
        #             count_of_each_var[var] += 1

def format_equation_for_csp_solver(x:int, y:int, variables:tuple, surrounding_mine_count:int) -> list:
    # NB! 'variables' has to be a tuple OR something that can be converted to a tuple
    variables = tuple(variables)  # if there's a cell with (x,y) = (4,5) in self.front, then the variable name shall be '(4,5)'. Simple and effective. The constraint for each variable is [0,1], meaning that the solution for each variable has to be 0 or 1.
    input_addition = [x, y, variables, surrounding_mine_count]
    return input_addition