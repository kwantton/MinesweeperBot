'''to-do:
- more tests, also on 'botGame.py' side
'''
from itertools import combinations
from time import time, sleep

class CSP_solver:
    '''
    Takes groups of boolean equations (where each variable is 0 or 1), solves them if possible, 
    and if cannot solve any variables, calculates the optimal guess (minesweeper cell = variable) and passes that
    info to botGame.py, where that safest guess is made (the safest cell is opened).

    An equation is for example a+b+c=2, which would mean that 3 cells, a b and c, together have 2 mines in them.
    That would mean that a=0 or b=0 or c=0 (0 = no mine, 1 = mine). This equation would correspond to a number
    cell with number 2, that is next to three unclicked cells (unclicked and unflagged in my case, to be specific).

    In the case of minesweeper, my variables are not a, b etc - they are (0,0), (0,1), (0,2) etc; (x,y).
    This also makes it possible to sort the variables in each equation, and sort equation sets
    so that an equation chain can be built within each separated equation set so that there is 
    overlap between each neighbouring link in the equation chain, discarding incompatible solutions between
    equations in the set as the linking is done.
    '''
    def __init__(self, mines_total = float("inf")):

        self.guess = None                                               # 12.10.24: The safest cell to guess is saved here for use in botGame.py, if there is a need to guess. If (1) normal solving doesn't help AND (2) mine counting doesn't help either, THEN guess the safest cell. This info, 'self.guess', is passed on to 'botGame.py' where the guess is made. I made a separate variable for this to be able to recognize this guessing situation in 'botGame.py' to distinguish it from normal solving; this makes it possible to add visuals, etc...
        self.choice = None                                              # either 'FRONT' or 'UNSEEN'; this tells you if the next guess is located next to 'self.front' (botGame.py has 'self.front') or in the cells unseen by self.front ('unseen unclicked')? This is for choice of guessing, and for passing this info to 'botGame.py' after the choice has been made. This is to describe it for printing.
        self.time_limit = 20                                            # NB! Here you can set max time limit for 'traverse()' in 'join_comp_groups_into_solutions()'. If no limit is set, the worst games will be killed automatically
        self.timeout = False
        self.variables = set()                                          # ALL variables, solved or not
        self.front_guess = None                                         # the safest front guess cell is saved here for use in botGame.py
        self.unique_equations = []                                      # { ((var1, var2, ..), sum_of_mines_in_vars), (...) }. Each var (variable) has format (x,y) of that cell's location; cell with a number label 1...8 = var. Here, I want uniqe EQUATIONS, not unique LOCATIONS, and therefore origin-(x,y) is not stored here. It's possible to get the same equation for example from two different sides, and via multiple different calculation routes, and it's of course possible to mistakenly try to add the same equation multiple times; that's another reason to use a set() here, the main reason being fast search from this hashed set.        
        self.p_success_front = None                                     # initialize. Otherwise 'draw' section in 'pyGame.py' complains that there's no such attribute. This is the highest probability that the most safe unclicked cell next to self.front is safe (has no mine).
        self.p_success_unseen = None                                    # initialize. Equal probability for each of the unclicked unseen cells to NOT be a mine at the moment
        self.solved_variables = set()                                   # ((x,y), value); the name of the variable is (x,y) where x and y are its location in the minesweeper map (if applicable), and the value of the variable is either 0 or 1, if everything is ok (each variable is one cell in the minesweeper map, and its value is the number of mines in the cell; 0 or 1, that is)
        self.mines_total = mines_total
        self.minecount_successful = False                               # used in 'botGame.py' for printing 'minecount successful' when it's used. Convenient for debugging!
        self.minecount_solved_vars = set()                              # for highlighting in botGame.py
        self.variable_to_equations = dict()                             # it's good to initialize this here too for rare cases. Dict: { variable 1 : all equations that contain variable 1, variable 2 : all equations that contain variable 2, .... }
        self.impossible_combinations = set()
        self.solved_new_vars_during_this_round = False

    def reset_variables_before_new_round_of_csp_solving(self):
        self.guess = None                                               # what is the next guess, if needed? If this is not 'None', then guess is needed. Resetting this to 'None' at the start of every round of 'absolut_brut()', in case the previous round was a guess. (12.10.2024): this is the default value. If even mine counting doesn't help, then this is set to True in 'handle_possible_whole_solutions()'. That info is then read in 'botGame.py' to handle the guessing.
        self.start = time()                                             # can use this to stop if takes a ridicilous amount of time per round
        self.choice = None                                              # the best possible front cell (lowest chance of mine in front) OR unseen unclicked cells? The guess is always one of these two
        self.front_guess = None                                         # save the safest possible front cell here if guess is needed
        self.p_success_front = None                                     # probability of surviving the safest front cell guess
        self.p_success_unseen = None                                    # prob of surviving any of the safest non-front cell (aka. unseen unclicked cell) guesses; they are equal, as they are unseen, so they all have the same (naive) probability
        self.minecount_successful = False                               # was a new solution found via minecount? This info is used in printing in 'botGame.py': write 'minecount successful' in the game, if minecount was used. For debugging, and most especially for showing off and looking smart.
        self.solved_new_vars_during_this_round = False                  # the most straightforward way of checking if guessing is ACTUALLY needed, as long as you remember to set this to 'True' when appropriate!

    # SOLVER ↓
    def absolut_brut(self, n_mines_remaining=-1, all_unclicked = [], 
        number_of_unclicked_unseen_cells = -1, unclicked_unseen_cells = []) -> None:   # minecounting logic is used ONLY if the minecount is not changing, i.e., if CSP_solver is currently incapable of solving any more of the map without minecount (not enough information -> 'normal' logic is not enough). In this situation, use information that unclicked_cell_1 + unclicked_cell_2 + unclicked_cell_3 + .... = total number of mines remaining in the entire map (HOWEVER! that equation is not used; it would be too slow, extremely slow at large numbers of unclicked cells remaining). In some cases, that helps solve the remaining situation, sometimes not.

        ''' 
        (0) `simple_solver()` in botGame.py is used as long as possible. When it can no longer solve new variables, perform 1-7 below (up until the point where new solutions have been found, don't go further if not needed)

        (1) group equations to sets (1.1 and 1.2); all the members of one such equation set share variables directly or indirectly with each other (indirectly means, via other equations in that set). That is, sets do NOT share variables with other sets, ever.
        (2) 'find_and_group_possible_answers_per_single_equation()': find all alt combinations of 1s PER EACH EQUATION (in each set, which doesn't matter at this step). Each equation MUST have ONE solution (i.e. each number cell on the minesweeper map). There are not too many combinations per equation, since the max length of an equation is 8 (8 variables max, usually 2-6, roughly speaking), and the max sum is 8 for any equation. Almost always these equations are a+b=1, or a+b+c=2, or c+e+f+g+h+j=3, or the like.
        (3) chain link equations: for each variable-separated set of equations, find compatible alt solutions in a chain of equations (practically, thanks to ordering, this chain starts from top left of the map and goes to right, then to next row!), filtering out those alternative answers (alt answers, alts) that are not compatible with adjacent equations, for each equation. Each group of alt solutions = one equation's alt solutions: from all of the alternative combinations of 1s and 0s that DO satisfy the CURRENT equation (group), filter out those alternatives that are incompatible with ALL alt answers from THE NEXT EQUATION IN THE ORDERED EQUATION CHAIN that is in the same equation set (shares variables directly or indirectly with other members of that equation set). This filters away impossible alt answers and helps building the solution trees in the next step (where conflicts are checked):
        (4) from the possibly ok (pair-filtered) alt equations per equation, build alt solution trees from the equation chain; the root is an alt answer for the starting equation, and during construction of these trees, conflicting variable value causes backtracking -> the branch (up until the last chance to go somewhere else than the current confilct) is discarded
        (5) for each eq set -derived bunch of alt solution trees, from the alt solutions, for each var record the number of times the variable value was 0, and the times it was 1. During this, also record the best-bet cell to guess in case a guess is needed later. In effect: find variables that were always 0 or always 1 -> those variables have been solved as 0 or 1 respectively. If can't find those, then you have the best guess cell from the front-seen cells, and if that chance of being mine is lower than unclicked unseen cells' chance of being mine, the best bet guess is the lowest-mine-chance front-seen cell, otherwise it's any of the unclicked unseen cells.
        (6) if didn't find variables that are always 0 or 1, check the need for minecount (it's quite simple at this point). If minecount can provide solutions (meaning, if max number of mines in `self.front` ≥ remaining minecount, which means that not all whole-front alt solutions are ok because some of them have TOO MANY MINES), use alt solution mine number counting to check, if the alt solution is ok or not. Once again, for each variable, record the count of var = 0 and var = 1, and if after this filtering-out of bad alt solutions a variable was ALWAYS 0, it has been solved as 0. If it was always 1, it's solved as 1.
            (6.1) if minecount doesn't help (= if max number of mines in `self.front` < remaining minecount, meaning that all alt solutions are ok regarding the number of mines in them), then guess. At this point, I've already
        (7) if nothing else above helps, if `self.solved_new_vars_during_this_round = False` at this point, then guess.
        '''
        
        print('\nabsolut_brut()')

        # used in `chain_link_equations()` below; are there common variables between two equations?
        def common_vars(vars1, vars2) -> bool:
            '''

            '''
            common = False
            varsB = set(var_val[0] for var_val in vars2)                              # twople = (var, value), but obviously I can't name it 'tuple' since that's reserved in Python
            for var_val in vars1:
                if var_val[0] in varsB:
                    common = True
                    break
            return common
        
        # (1.1) find separate sets of vars; this is for significantly reducing the max number of combinations of alt solutions per set later. If they are NOT separated whenever possible, the number of alt solution candidates (which are combinations) increases ~exponentially (why ~; because one separate set can have 2 alt solutions, the other 3, the third only 1, ect, so it's ON AVERAGE exponentially)
        def divide_vars_to_disconnected_sets() -> dict:                             # finds sets that do not share a single variable between the var sets. For example a+b=1 and b+c=1 would be one equation set, separate from e+f+g=2, if there was only those three equations in total in self.unique_equations.

            called_vars = set()
            grouped_vars = set()
            groupN_to_vars = dict()                                                 # group_n : {var1, var2, var3..}
            completely_grouped_eqs = set()

            def add_eqs_containing_current_var_to_current_group(group_n, variable):
                if variable in called_vars:                                         # this function will pass this check (i.e. will NOT return) exactly as many times as how many UNIQUE variables there are; if a,b,c,d, then 4 times in total, no more. Quite practical.
                    return
                next_up = self.variable_to_equations[variable]
                called_vars.add(variable)
                for vars, summa in next_up:
                    for var in vars:
                        if var not in grouped_vars:
                            groupN_to_vars[group_n].add(var)
                            grouped_vars.add(var)
                    if (vars, summa) not in completely_grouped_eqs:                 # this 'if' is technically not needed, but good for debugging
                        completely_grouped_eqs.add((vars, summa))
                    for var in vars:
                        add_eqs_containing_current_var_to_current_group(group_n, var)

            group_n = 1
            for key, eqs in self.variable_to_equations.items():
                if len(called_vars) == len(self.variables):                         # if ALL the variables have been classified, then return. Usually, this return happens after the first round, if all the variables are connected! This saves quite a bit of work. This saves a LOT of work later on when connecting equation pairs, and when building solution trees; I'm keeping separate groups separate!
                    return groupN_to_vars
                groupN_to_vars[group_n] = set()                                     # initialize for this 'group_n'
                for variables, summa in eqs:
                    for var in variables:                                           # add all vars to current group
                        if var not in grouped_vars:                                 # if one of these is not present, then none should be! The 'add_eqs_to_current_group' below might have added these already. If it has, then DON'T make another group
                            add_eqs_containing_current_var_to_current_group(group_n, var)
                group_n += 1
            return groupN_to_vars
        
        # (1.2) from disconnected variables above, build disconnected (separate) sets of equations
        def build_separate_sets_of_equations_from_separate_sets_of_vars(setN_to_vars) -> list:
            '''
            returns: list of 'separate sets' of equations. Each separate/disconnected set of equations shares 0 variables with any other set. The purpose is to divide all the equations into separated sets so that they can be handled separately, so that the max size of combinations in alt answers per set of equations is significantly reduced later -> better time complexity
            '''
            separate_sets_of_vars = [setti for setti in setN_to_vars.values()]          # I no longer need the setN (arbitrary equation set number, which was useful in the function, but is no longer needed for anything at all). In the first 8 tests, there's just one 'separate' set, meaning that all the variables are connected. In real minesweeper, especially in expert, you frequently see more than one separate set of equations, meaning that one set's mine locations do not directly affect the other's logic in any way.
            separate_sets_of_eqs = []
            for set_of_vars in separate_sets_of_vars:
                eqs_of_this_set = set()
                for var in set_of_vars:
                    eqs_for_var = self.variable_to_equations[var]
                    for eq in eqs_for_var:
                        eqs_of_this_set.add(eq)
                separate_sets_of_eqs.append(eqs_of_this_set)
            return separate_sets_of_eqs

        # (2) for each separate set (set=joukko) of eqs, for each equation (i.e. each number cell on the minesweeper map), given that each variable (= each unopened cell) is 0 or 1 (no mine or a mine), find all possible combinations of 1s and 0s that can satisfy that SINGLE equation GIVEN THAT it has sum = k (some integer number = the number of mines in those unopened surrounding cells in total!)
        def find_and_group_possible_answers_per_single_equation(sets_of_eqs:list) -> list:
            '''
            returns: for each separated set of equations, for each equation in that set, 
            get possible combinations of mines in format [ [] ]. Here each inner list has tuples of tuples of tuples, 
            where each innermost tuple is ('x':0) or ('x':1) or such; possible values for the variable 
            given the constraints of that specific equation.
                Each tuple surrounding this innermost tuple consists of all variables and their values in that equation. 
            And the outermost tuple (3rd) has all the variations (alt solutions) for that equation, 
            as tuples of tuples of values for variables. Easier to see using debugger!
            '''
            alt_answers_for_groups = list()
            for set_of_eqs in sets_of_eqs:
                alt_answers_per_equation = []
                for variables, summa in set_of_eqs:                                     # so (variables, summa) is one equation, in a 'set of eqs'
                    mine_location_combinations = combinations(variables, summa)         # all possible combinations of mines for this equation. Since all incoming equations are of form a+b+c=1, and each variable is 0 or 1, I'm here just picking the MINE cells; combinations of mine cells.
                    this_eq_group = []                                                  # NB! All the possible solutions for THIS equation ('variables', 'summa' constitutes an equation in 'self.unique_equations') are gathered here; in the end, I have to solve each of these 'individual' equations, AND find a solution that satisfies all the other equations as well.
                    for mine_location_combination in mine_location_combinations:
                        combo = []                                                      # for all vars a,b,c,... {a:1, b:0, c:0, ....}
                        for var in sorted(variables):                                   # I want to always handle variables in alphabetical order so that I can be sure that when I read/write into data structures according to combinations of variables, then for example a dict key (a,b,c) is always (a,b,c), not (b,c,a) or something else. This is to reduce unnecessary computing and to keep things overall as simple and reliable as possible.
                            if var in mine_location_combination:
                                combo.append((var, 1))                                  # I could add only the 1s as all the others are 0, BUT then I'd have to also gather a set of all the variables present. Instead, I like to keep it more visually clear here; also each 'combo' is short, so using a set vs. iterating through all (usually 2-4) items makes no big difference performance-wise
                            else:
                                combo.append((var, 0))
                        combo = tuple(combo)                                            # (('a',1),('c',0),...) is the format of combo
                        this_eq_group.append(combo)
                            
                    alt_answers_per_equation.append(tuple(this_eq_group))               # each list in this list is a list of alternative answers for that equation in question
                alt_answers_for_groups.append(alt_answers_per_equation)
            return alt_answers_for_groups
        
        # (3) for each separated set (set=joukko) of equations, do the following: for each group (group=alternative solutions for ONE equation like a+b=1 ('a' is a cell on the minesweeper map, 'b' is another cell)), find at least one solution that's compatible with AT LEAST ONE alternative solution from EXACTLY ONE other group (reminder: group = group of alt solutions for an equation). So, connect the first equation (group) to ONE another equation (second 'group'), and that also to another group, and so on (=build a chain of groups = a chain of compatible alt answers). So, for all compatible alt solutions in the 2nd group, couple all of those to the 3rd group (i.e. to the next equation); this builds a chain of equations, where all neighbouring alt solutions are compatible, where the first equation is linked to one equation, the next one to the previous and to the next, etc, and the last one is linked only to the previous one. AFTER 'chain_link_equations', continue to build all possible alternative answers from those, so that there's bookkeeping for every variable for every possible unique alt whole-solution, so that if a conflict is found, building of that alt solution tree is terminated on the spot -> less computation wasted. I think this was called backtracking, as I later found out.
        def chain_link_equations(alternative_answers_per_equation_per_set_of_eqs:list) -> list:
            '''
            returns: list of tuples 
            [ (equation set 1's "compatibility groups", starting equation for these compatibility groups), (equation set 2 ...) ...]
            What does a compatibility group mean: Each alt answer for equation A
            is called altA. For each altA, `compatibility_groups[altA] = set()` which consists of those
            altBs (alternative answer for equation B, which is next in the chain of equations for the set in question)
            which do not conflict with altA. So for example if altA is a=0, b=0, c=1,
            then if altB is b=1, c=0, then altB would not be in altA's compatibility group as it conflicts.
            It could be in another altA's compatibility group. All these are gathered into 'compatibility_groups'
            dict().

            Only those altAs remain that were compatible with at least one altB from equation B (='groupB').
            Likewise; only those altBs remain that were compatible with at least one altA.

            Then the altBs that were ok become the new altAs for the second round; so each non-terminal equation
            is filtered through two adjacent equations this way.

            Then later, this filtered chain of equations (for each separated equation set!) is fed to a
            whole-chain conflict finder, which is a tree where the origin is an alt solution for the starting
            equation, and backtracking is done (branch discarded) in the case of conflicting variable values.
            '''
            print('chain_link_equations()')
            
            comp_groups_and_starting_groups = []
            for alternative_answers_per_eq in alternative_answers_per_equation_per_set_of_eqs:
                alternative_answers_per_eq = sorted(alternative_answers_per_eq) # using `sorted()`, try pairing equations with max overlap; essentially, keep them in coordinate-adjacent order, that's it
                compatibility_groups = dict()                                   # { possible solution : all related possible solutions (i.e. those which share variables and do not disagree for any variable value for those variables that are present in both the key and each of the values in this dictionary for that key!) }. There's no need for explicit bookkeeping regarding which of the value solutions belong to which original equation, because the variables included themselves are enough to identify the origin.

                for a in range(len(alternative_answers_per_eq)):                # e.g. ( (('a',0), ('b',1)), (('a',1),('b',0)) ) would constitute one 'group' (length 2) for the equation 'a+b=1' which is stored as ((a,b),1) in 'self.unique_variables'; that is, all the possible solutions for that equation constitute a 'group'
                    if a == 0:
                        groupA = alternative_answers_per_eq[a]
                        starting_group = alternative_answers_per_eq[a]
                    else:
                        groupA = sorted(tuple(next_round_groupA))               # from the previous round! Since this is from a set, it may become disordered -> for comparison if equal with groupB, sorting is needed!
                    if a == len(alternative_answers_per_eq)-1:                  # NB! See comment below. Here, I need to add the keys also for the last groupA even though it has no groupB to pair it with. This is because checks in 'traverse()' later require the existence of at least one viable alt per group in the keys of 'compatibility_groups', for EVERY group (i.e. for all original equations from the minesweeper map)
                        for alt in groupA:
                            compatibility_groups[alt] = set()                   # all viable alts must be found in keys of 'compatibilty_groups'. On the last round, groupA consists of the compatible alt solutions of last round's groupB, and these are all ok. Therefore, all of them must be added to 'compatibility_groups'.
                        break
                    b = a+1
                    groupB = alternative_answers_per_eq[b]
                    if groupA==groupB:
                        continue                                                # This never happens (GOOD! This is currently the expected result). It should NEVER happen as long as I don't change this whole function (again...).
                    next_round_groupA = set()
                    common_variables = common_vars(groupA[0], groupB[0])        # I want unilateral direction to ALL possible compatible alt solutions from ALL OTHER groups
                    at_least_1_altA_compatible_with_groupB = False              # Default. NB! groupB needs to be compatible for altA to be viable! That is: if altA is to be viable, it has to satisfy at least one altB from every groupB! (2) this ALSO checks if there are
                    n_compatible_altBs = 0                                      # If from the entire groupB we end up with just ONE altB that's compatible with groupA, then it IS THE ONLY POSSIBLE ANSWER (=the only viable altB) FOR THAT groupB IN QUESTION beause every single equation (each groupA and groupB) must have at least one compatible solution with each other -> altB therefore provides UNIVERSALLY THE ONLY POSSIBLE (combination of) VALUE(s) FOR EACH OF altB's VARIABLES -> mark all those as solved
                    for altA in groupA:                                         # E.g. altA = (('a', 0), ('b', 1)); altA = alternative solution (i.e. ONE theoretically POSSIBLE solution) to the equation whose possible answers are members of groupA; altA = one alternative solution for a single equation, that might or might not be possible (i.e. might or might not be compatible with each groupB (i.e., with at least one possible answer of each other equation))
                        compatibility_groups[altA] = set()
                        for altB in groupB:                                     # NB! ONE at least needs to be compatible with altA, OR altA is not 'viable_and_connected'. e.g. (('a', 0), ('b', 1)); alt = alternative = one alternative solution for a single equation, that might or might not be possible (i.e. might or might not be compatible with A)
                            altA_altB_compatible = True                         # default
                            if common_variables:                                                                  
                                for var, val in altA:                           # e.g. 'a', 0. Each var1, val1 has to be compatible with at least ONE alt2 from every other group, so that 'altA_is_viable'!
                                    opposite_value = (var, int(not val))        # val = 1 or val = 0; if 1, opposite = (var, 0). This is so I can avoid if-clause below, making it shorter.
                                    if opposite_value in altB:
                                        altA_altB_compatible = False
                                        break
                            if altA_altB_compatible:
                                n_compatible_altBs += 1
                                at_least_1_altA_compatible_with_groupB = True
                                compatibility_groups[altA].add(altB)            # I don't need to explicitly group this altB for this key; I know that those values which share the same variables belong to the same group (i.e. they originate from the same equation)!
                                next_round_groupA.add(altB)                     # on the next round, these ok altBs become groupA c:
                        
                        # THIS IS PER altA! It's completely OK if the code goes here, it reduces time complexity later on; if the current altA is not compatible with any altB from the current groupB, that means that the altA is not compatible AT ALL with groupB (= any alt answer of equation B). If that happens, then the altA is deleted from the 'compatibility_groups', because it's an impossible combination of variable values (it can never satisfy groupB, i.e. equation B, but we KNOW that equation B MUST be satisfiable, so altA is in that situation impossible).
                        if not at_least_1_altA_compatible_with_groupB:          # if altA from groupA is viable, it will have added groups of viable altBs from every other group
                            del compatibility_groups[altA]                      # do not keep lonely equations in the dict 'compatibility_groups'
                            # NB! DO NOT 'break' here! The unchecked altAs that are still remaining in the loop might be compatible solutions, so running 'break' here is NOT correct.
                        else:                                                   # if there are no shared variables between groupA (including altA) and groupB (including altB), then groups A and B ARE compatible (they don't restrict each other in any way) -> move on to next groupB
                            at_least_1_altA_compatible_with_groupB = True       # just to show what this means in reality! Writing clear the logic for future generations... or myself, maybe.
                            continue                                            # this means that entire groupA and groupB are compatible -> move on to the next altA (moving on to next GROUP A would be even better though)

                comp_groups_and_starting_groups.append((compatibility_groups, starting_group))
            return comp_groups_and_starting_groups
        
        # every key in 'compatibility_groups' is an alt solution for one equation that must be solved one way or another. The same goes for all equation groups in each of those keys' values, BUT here I'm just looking at the keys before looking at their values.
        def keyVars_to_keys_builder(compatibility_groups:dict) -> dict:
            keyVars_to_key = dict()                                             # let's say there are 2 alt versions (two possible ALTERNATIVE solution vectors, e.g. (a) a=1, b=0, c=1 and (b) a=1, b=1, c=0, that survived the previous handling in 'restrict_solution_space_as_equation_pairs_with_common_variables()') for an equation (a+b+c=2 in this example). These 2 alternative solution vectors share all the same keyVars (a,b,c). We know that ONE of these alt vectors has to be true. So, if in both alt versions, a variable has value 0, then that variable MUST be 0. If both have a variable value 1 (a=1 in both alt solutions in my example!), then that variable MUST be 1. This is because this equation, as well as every other equation originating from a cell in the minesweeper map, has to be satisfied (because all of them are true!), so exactly one of its alt vectors has to be true.
            for key in compatibility_groups.keys():                             # e.g. key = (('a',0),('b',1),('c',1)), values are similar, AND each value for each key shares at least one variable (like 'a') with the key (which is also an equation, just like the values)
                key_vars = tuple(proposed_value[0] for proposed_value in key)   # NB! THese still are in alphabetic order, thanks to 'itertools.combinations' in 'find_and_group_possible_answers_per_single_equation' which sorted the answers alphabetically
                if key_vars not in keyVars_to_key:
                    keyVars_to_key[key_vars] = []
                keyVars_to_key[key_vars].append(key)
            return keyVars_to_key
        
        def identify_group(proposed_matching_alt_solution:tuple) -> set:        # the 'vars' set is a set of the variables present in the 'alt_solution'; this is for bookkeeping of which groups (i.e. equations, with one or more alt answers) have already been handled and which not. All groups must be found exactly one alt solution for!
            vars = set()
            for var, value in proposed_matching_alt_solution:
                vars.add(var)
            return vars

        def check_for_disagreements(proposed_matching_alt_solution:tuple, possible_solution_build:dict) -> tuple:
            incompatible_pma = False
            for var, value in proposed_matching_alt_solution:                       # (('a',0), ('b',1), ...) a 'proposed_matching_alt' has this format. It's one alt solution to an equation that's derived from the minesweeper map and which has to have ONE alt solution, the other ones being untrue.
                if var in possible_solution_build:
                    if possible_solution_build[var] != value:
                        incompatible_pma = True
                        break                                                       # it's possible that one or more variable values from an alt answer (the current one) disagree with one or more alt answers that are INDIRECTLY connected to the current alt answer. Hence, they are in this case 'incompatible' (they directly disagree with each other), and the handling of this current alt solution should be prevented altogether
            return incompatible_pma
        
        def timeout_guess():                                                        # here's the possibility to use a timer; in case it takes too long, guess either the optimal unclicked unseen cell, OR a random cell
            self.guess = 'timeout'
            return
        
        # (4) done: smarter solution inspection directly via var values instead of via going through every alt solution again
        def join_comp_groups_into_solutions(compatibility_groups:dict, starting_group) -> tuple:     # also return the whole list of 'possible_whole_solutions'; it's needed IF minecount is needed. If minecount is needed
            print('join_comp_groups_into_solutions()')
            keyVars_to_keys = keyVars_to_keys_builder(compatibility_groups)
            n_groups = len(keyVars_to_keys.keys())
            value_counts_for_each_var = dict()  # done: COUNT HERE, FOR EACH VAR, HOW MANY TIMES 0 AND HOW MANY TIMES 1 it is in minecount-OK alt solutions. SOLVES ALSO PROBLEMS REGARDING GUESSING! If the var has only 1s, then it's solved as 1. If only 0s, then it's solved as 0. Otherwise, the probability is extremely straightforward to calculate!
            possible_whole_solutions = []
            n_times_traversed_for_debugging = [0]
            
            def traverse(this_alt, entered_alts_for_this_build, 
                possible_solution_build, already_handled_groups,
                n_times_traversed_for_debugging) -> None:                                # returns 'n_times_traversed...'

                elapsed = time() - self.start
                if elapsed > self.time_limit:
                    self.timeout = True
                    return
                n_times_traversed_for_debugging[0] += 1

                already_handled_groups_local = already_handled_groups.copy()
                possible_solution_build_local = possible_solution_build.copy()
                entered_alts_for_this_build_local = entered_alts_for_this_build.copy()                
                
                if this_alt in compatibility_groups:                                    # If this alt solution is not a key in 'compatibility_groups', then IT IS UNTRUE as it's incompatible with one or more other groups' every possible alt answer; in that case, do NOT handle this alt at all (do not (1) mark its variables' proposed values as possible solutions, and do not (2) mark the group that it presents as handled); if the current alt is NOT present as a key of 'compatibility_groups', IT IS INCOMPATIBLE WITH AT LEAST ONE OTHER GROUP. In English, if the current alt solution is not present as a key in 'compatibility_groups', it CANNOT EVER SATISFY ALL THE EQUATIONS that we know MUST be true using at least one combination of alt solutions.
                    group_of_this_alt = identify_group(this_alt)                        # 'this_alt' is an alt answer for some group - 'identify_group(this_alt)' tells me WHICH group it belongs to. I want EXACTLY ONE alt answer for EACH group, as each group represents an original equation from the minesweeper map (a number cell, the equation of which is always true, so MUST be satisfied and MUST be compatible with all other groups!)
                    if group_of_this_alt not in already_handled_groups_local:           # NB! So, I only want EXACTLY ONE alt solution per group. If an alt solution has already been handled, DO NOT HANDLE ANOTHER; that another alt solution will be handled in a whole another iteration of this 'traverse()'. (2) Comparison of sets in python; if the values in the set are the same, then the sets are 'equal' in the == comparison. Nice.

                        incompatible_alt_solution = check_for_disagreements(            # this cannot happen on the FIRST call of 'traverse()', but it CAN happen on subsequent later calls - the 'compatibility_groups' only ensure PAIR compatibility, not beyond than that!
                            this_alt, possible_solution_build_local)
                        if incompatible_alt_solution:                                   # if this alt solution disagrees i.e. is incompatible with already-recorded alt solutions (one from each met group so far), then move on to the next 'proposed_matching_alt' (which may be of the same OR of different group!) NB! Do NOT mark the group of the current alt solution as handled if it's incompatible; this means that we still need to wait for a compatible alt to come by from this group, so I must NOT mark it as handled yet!
                            return

                        # this includes the current alt solution
                        for var, value in this_alt:                                     # (('a',0), ('b',1), ...) a 'proposed_matching_alt' has this format. It's one alt solution to an equation that's derived from the minesweeper map and which has to have ONE alt solution, the other ones being untrue.
                            possible_solution_build_local[var] = value                  # there can be 1 or 2 per variable. If 2, it means that there is not enough information (yet) for solving this variable. If only 1 value, great, that means the value is now solved.
                        
                        already_handled_groups_local.append(group_of_this_alt)          # Since the alt solution was picked, mark the respective group as handled. ATM this is unnecessary, since I'm traversing through the equations in the same chain order as they were linked earlier, but If I were to change that, then this check is needed (previously, I DID need this, but this is a good check also for debugging anyways!)

                        if n_groups == len(already_handled_groups_local):
                            for var, value in possible_solution_build_local.items():
                                if var not in value_counts_for_each_var:
                                    value_counts_for_each_var[var] = [0,0]              # [0s, 1s] seen so far
                                if value == 0:
                                    value_counts_for_each_var[var][0] += 1
                                else:
                                    value_counts_for_each_var[var][1] += 1
                            possible_whole_solutions.append(possible_solution_build_local)
                            return                                                  # if it's done, it's done. The possible next matches would be to a completely different group, AND it's not possible to gain more solutions from this one, as new groups and their alts are only ADDED in this 'traverse()', not removed, and we've already been to all groups -> return, don't continue!

                        new_matches = compatibility_groups[this_alt]                    # continue to matches of this alt solution ONLY if none of the values of this alt solution disagree with values that have already been recorded in 'possible_solution_build' as values of the variables
                        entered_alts_for_this_build_local.add(this_alt)

                        # only do this if the above has not been fulfilled; it's not possible to gain another answer by trying to add yet another alt solution in the case where all the equations (all groups) have already been satisfied, which is checked in the 'if' clause above. SO: for every set of new_matches, I want the info that was updated according to what happened in the specific alternative solution above; which alt solution ('proposed_matching_alt') was 'entered' (seen, processed), which 'group' (equation) in question was handled. Since all the alternatives in the above loop are indeed ALTERNATIVES, they are NOT all saved immediately! (that would be incorrect), instead that is done after the 'traverse()'s below!
                        if new_matches:
                            for new_match in new_matches:
                                if new_match not in entered_alts_for_this_build_local:    # technically redundant, probably almost no effect regarding computing efficiency, BUT it's nice for clarity, and showing the logic still (even if double check)
                                    traverse(new_match, entered_alts_for_this_build_local, 
                                        possible_solution_build_local, already_handled_groups_local,
                                        n_times_traversed_for_debugging)
                                    if self.timeout:
                                        return
                        
            # 'starting_group' is the group from where all arrows leave, and back to which no arrows return; an alt origin for an alt rooted tree, essentially!
            for alt_origin in starting_group:                                       # E.g.: ('d', 'e'), [(('d',1),('e',0)), (('d',0),('e',1))]. This quarantees that they build unidentical solution trees that together encompass all possible whole solutions.
                if alt_origin in compatibility_groups:                              # some might have been filtered out as they were no longer fitting ALL other groups; the whole key has been deleted from 'compatibility_groups' if it's not compatible with ANY alt solution from its paired group (paired equation)
                    seen_proposed_vectors = set()                                   # PER alt answer, of course - that's why it's initialized here and not at the top of this 'join_groups_into_solutions'
                    handled_groups = []
                    alt_solution_build = {}
                    traverse(alt_origin, seen_proposed_vectors, 
                        alt_solution_build, handled_groups, n_times_traversed_for_debugging)                         # 'traverse' builds alternative 'possible_whole_solutions' and saves all viable ones to 'possible_whole_solutions'
                    if self.timeout:
                        timeout_guess()
                        print('TOOK LONGER THAN', self.time_limit, 's - therefore GUESSING NEXT')
                        return 'time', 'out', 'occurred'
            
            # done: Count also at this point, use the ready function for that!; if max mines in front < minecount, there's NO NEED for minecount (this is checked in minecount situation checking functions later) -> use this instead!!!! That will significantly make the worst cases faster!!
            print('- traverse()s finished,', n_times_traversed_for_debugging, 'times in total')
            best_bet, highest_survival_rate_in_front_cells = handle_minecount_results(
                value_counts_for_each_var)
            return possible_whole_solutions, best_bet, highest_survival_rate_in_front_cells

        # (6) guess if needed. NB! this 'best' guess considers this round only; it doesn't take into account what will happen later
        def choose_best_guess(naive_safest_guess, min_n_mines_in_front, best_front_chance):
            print('choose_best_guess():')                                       # NB! This can happen both before it's known if a guess is actually needed (before minecount check, which checks if minecount would be useful, because performing this function is very quick and convenient), and AFTER minecount, if we know that guessing is ABSOLUTELY needed as minecount didn't help. That is; this function is called either 0, 1 or 2 times per round of 'absolut_brut()'. If it happens 2 times, it is KNOWN that these results will be used for guessing. If 1 time, then either they are used (if minecount isn't useful) or not (if minecount IS useful and provides answers)

            self.choice = 'FRONT'                                               # default
            self.guess = naive_safest_guess                                     # default. The below might be false -> the default stays.
            self.front_guess = naive_safest_guess                               # as a backup to 'botGame.py' in case there are no unseen cells at all
            if number_of_unclicked_unseen_cells > 0:                            # Can't guess unseen cell if there are no unseen unclicked cells.
                unclicked_unseen_cell_safety_in_worst_scenario = 100 - (100 *(n_mines_remaining - min_n_mines_in_front) / number_of_unclicked_unseen_cells)  # 100 - percent mine density in unclicked unseen cells in the case that there's the minimum possible number of mines remaining in self.front. It's arbitrary that I chose to inspect the worst case scenario, but generally speaking it's better to opt for guessing cells of partially-known situations than random whatever-tiles in many situations, since often guessing near the front has a higher chance of uncovering more logically solvable situations. However, as that depends on pretty much everything, I repeat that this is NOT the optimal solution in many cases!
                if best_front_chance < unclicked_unseen_cell_safety_in_worst_scenario:
                    self.guess = "pick unclicked"                               # for guessing. If 'unclicked' cells have the lowest mine density, then guess there. 
                    self.choice = 'UNSEEN'
                self.p_success_unseen = round(unclicked_unseen_cell_safety_in_worst_scenario, 1)
                if self.p_success_unseen < 0:
                    # Note: this can be negative! Note the 'MIN' in 'min_n_mines_in_front'? In cases where minecount doesn't exactly tell how many mines are in uu cells, it's possible that the min n mines IS INDEED impossible, BUT still taking that into account doesn't lead to new absolute solutions for any variable -> this guessing is called -> a negative number can be printed here, because I'm using the WORST CASE SCENARIO. That's why "≥" is written in the game in showing the uu probability ('uu prob ≥ x', written as 'other ≥ x' in the game)! Yes, this is complicated, sorry.
                    print("p_success_unseen < 0:", self.p_success_unseen)
                    # raise ValueError("p_success_unseen < 0:", self.p_success_unseen)
                    sleep(10) # I wanted to inspect these cases, they are ok. Read the comment above, 'Note: ...'
                print("- p_success(unseen) ≥", self.p_success_unseen, '%')
            self.p_success_front = round(best_front_chance, 1)
            print('- p_success(front)  ≤', self.p_success_front, '%')
            print('- guess:', self.choice)

        def handle_minecount_results(value_counts_for_each_var:dict, min_n_mines_in_front = -1) -> tuple:
            '''
            Parameter 'value_counts_for_each_var' (dictionary) is exactly what it says:
            for each variable, it's been counted before calling this equation, how many times it was
            0 and how many times it was 1 in the alt solutions. If only 0s are recorded for the variable,
            then it's solved as 0. If only 1s, it's solved as 1.

            Else, if no variable is solved this way, then the lowest-rate 1 variable is chosen for guessing,
            unless unclicked unseen cells have lower mine probability (in the worst case minecount situation, btw).
            (note: equations do not "see" 'unseen unclicked' cells, that's why I'm calling them that)
            
            ('in the worst case minecount situation' means, assuming highest mine density in unclicked unseen cells, 
            which means lowest possible total number of mines in cells seen by self.front.
            In most situations, the number of mines
            seen by 'self.front' of botGame is not constant; there could be 5 mines remaining in those cells that are 
            seen by the front, or 7, for example. In those cases, assume that the mine density in uu cells 
            is the highest, i.e. assume the lowest minecount seen by self.front - this is an arbitrary decision,
            but it slightly favours guessing in self.front, which could be a better strategy, as guessing in the 
            front safest spot often reveals solutions (no quarantee of that though!))
            '''
            best_bet = None
            from_minecount = True
            if min_n_mines_in_front == -1:
                from_minecount = False
            var_to_survivalChance = dict()
            highest_survival_rate_in_front_cells = 0

            for var, [zeros, ones] in value_counts_for_each_var.items():
                if zeros == 0:
                    if from_minecount:
                        self.minecount_successful = True                # used for printing 'minecount successful' in 'botGame.py'
                        self.minecount_solved_vars.add((var,1))         # for highlighting in botGame (visuals), bookkeeping  
                    self.solved_new_vars_during_this_round = True
                    self.solved_variables.add((var, 1))
                elif ones == 0:
                    if from_minecount:
                        self.minecount_successful = True                # used for printing 'minecount successful' in 'botGame.py'
                        self.minecount_solved_vars.add((var,0))
                    self.solved_new_vars_during_this_round = True
                    self.solved_variables.add((var, 0))
                elif not self.solved_new_vars_during_this_round:
                    var_to_survivalChance[var] = zeros / (zeros + ones)   # it's not possible that zeros+ones = 0 ever, IF talking about minesweeper, because of how the dict 'value_counts_for_each_var' was constructed.
                    if (zeros / (zeros + ones)) > highest_survival_rate_in_front_cells:
                        best_bet = var
                        highest_survival_rate_in_front_cells = zeros / (zeros + ones)

            if min_n_mines_in_front != -1: # NB! it's only -1 if 'handle_minecount_results()' was called NOT from minecount, but instead from after (4), which means I don't want to guess just yet, since the need for minecount hasn't been checked yet! If it's NOT needed (= if it doesn't benefit me), THEN I'll use this guessing c:
                if not self.minecount_successful:
                    print("Minecount done, didn't find solutions, NEED TO GUESS:")
                    choose_best_guess(naive_safest_guess = best_bet, min_n_mines_in_front = min_n_mines_in_front,
                        best_front_chance = highest_survival_rate_in_front_cells*100)
                else:
                    print("✔ Minecount was successful")
            else:
                return best_bet, highest_survival_rate_in_front_cells * 100

        # For every eq set: 'sets_altSolutionsMinminesMaxmines', get possible sums of mines, and count the number of times every alt is seen in any combination with others - this will be used in guessing, if needed ((If possible, return 'nMines_to_frontAltSolutions' like it was before.))
        def check_minecount_need_and_guess_or_minecount(sets_nMinesToAltsolutions_minmines_maxmines:list,
            smallest_n_mines_in_front_alt_solutions:int, largest_n_mines_in_front_alt_solutions:int,
            best_guess, survival_chance:int) -> dict:   # 0 <= survival_chance <= 100. Best_guess is the variable that, from cells seen by self.front, has the lowest chance of being a mine.

            def count_front_sums_to_get_ok_set_alts(only_min_ok = False, only_max_ok = False) -> dict:

                value_counts_for_each_var = dict()  # COUNT HERE, FOR EACH VAR, HOW MANY TIMES 0 AND HOW MANY TIMES 1 it is in minecount-OK alt solutions. SOLVES ALSO PROBLEMS REGARDING GUESSING! If the var has only 1s, then it's solved as 1. If only 0s, then it's solved as 0. Otherwise, the probability is extremely straightforward to calculate!
                n_sets = len(sets_nMinesToAltsolutions_minmines_maxmines)                                     # for checking if 'index' has reached the end; for building entire solutions

                # 'current_build' can be a list, the indices of which will tell, what the original set was; if the whole build is ok, then to each separate eq_set_ok_alts, add the ok alt solution of that set. Why: most importantly, combined to whole-front alt solution combination building, this enables (1) usage of 'handle_possible_whole_solutions' for every SEPARATED set on their own, (2) it's using the already-built minecount dictionaries per separated set pretty efficiently, reducing work further; discarding bad whole solutions is done based on sums alone, not needing to build and count every whole-front solution first. Downside; I'll have to make adjustments to the probability calculations of 'handle_possible_whole_solutions()', tracking global max probability of not being a mine, and whatnot, iterating the process for every alt set.
                def alt_solution_minecount_build_and_check(current_build:list, 
                    current_sum:int, current_index:int) -> None:

                    if current_sum > n_mines_remaining:                                                     # if the current sum of mines in the current build so far exceeds the number of mines remaining in the map at the moment, the the current build is impossible - stop building it.
                        return
                    if current_index == n_sets:
                        if current_sum + number_of_unclicked_unseen_cells < n_mines_remaining:              # Example: 8a. Any alt for which this happens is impossible. The max number of mines in 'unclicked unseen cells' is the number of those cells. So if this alt solution + that is less than the actual remaining minecount, then it's impossible
                            return # impossible whole-alt; too few mines
                        else:
                            # -> this front alt (whole-alt) is minecount-ok -> record the values of variables
                            for index in range(n_sets):
                                eq_set_alt_solution = current_build[index]
                                for var, value in eq_set_alt_solution.items():
                                    if var not in value_counts_for_each_var:
                                        value_counts_for_each_var[var] = [0,0]                      # 0, 1; counts how many times each
                                    if value == 0:
                                        value_counts_for_each_var[var][0] += 1
                                    else:
                                        value_counts_for_each_var[var][1] += 1
                    else:
                        next_set_nMines_to_altSolutions_minmines_maxmines = sets_nMinesToAltsolutions_minmines_maxmines[current_index] # the 'current_index' starts from 1, so this is not +1!
                        next_set_nMines_to_setAltSolutions, next_set_minmines, next_set_maxmines = next_set_nMines_to_altSolutions_minmines_maxmines
                        for next_set_nMines, next_set_altSolutions_with_nMines in next_set_nMines_to_setAltSolutions.items():
                            if only_min_ok:
                                if next_set_nMines != next_set_minmines:
                                    continue
                            elif only_max_ok:
                                if next_set_nMines != next_set_maxmines:
                                    continue
                            for next_set_altSolution in next_set_altSolutions_with_nMines:
                                new_build = current_build.copy()
                                new_build.append(next_set_altSolution)
                                alt_solution_minecount_build_and_check(current_build = new_build, 
                                    current_sum = current_sum + next_set_nMines, current_index = current_index + 1)

                # for nMines_to_setAltSolutions, min_minecount, max_minecount in alt_set_SolutionsMinminesMaxmines:
                first_set_nMines_to_altSolutions_minmines_maxmines = sets_nMinesToAltsolutions_minmines_maxmines[0] # each index, like this first one [0], in this list is all the altSolutionsMinminexMaxmines for that set; a triple (altSolutions, Minmines, Maxmines) for that eq set. All the altSolutions are in [0] of that triple.
                set_1_nMines_to_setAltSolutions, set_1_minmines, set_1_maxmines = first_set_nMines_to_altSolutions_minmines_maxmines
                for nMines, set_1_altSolutions_with_nMines in set_1_nMines_to_setAltSolutions.items():
                    if only_min_ok:
                        if nMines != set_1_minmines:
                            continue
                    elif only_max_ok:
                        if nMines != set_1_maxmines:
                            continue
                    for set_1_altSolution_with_nMines in set_1_altSolutions_with_nMines:
                        alt_solution_minecount_build_and_check(current_build = [set_1_altSolution_with_nMines], 
                            current_sum = nMines, current_index = 1)
                return value_counts_for_each_var

            # let's check the convenient cases first - it saves a lot of work with little cost, if one of these two is true
            only_min_sum_is_ok = only_max_sum_is_ok = False
            
            if smallest_n_mines_in_front_alt_solutions == n_mines_remaining:                # if none of the alt solutions have less mines than the currently remaining minecount, then all the unclicked unseen cells, which are NOT a part of any of these alt solutions, must NOT have a mine, otherwise the total minecount would exceed the REAL total minecount!
                only_min_sum_is_ok = True
                if number_of_unclicked_unseen_cells > 0:
                    for cell in unclicked_unseen_cells:
                        self.minecount_successful = True
                        self.solved_variables.add((cell, 0))
                        self.minecount_solved_vars.add((cell, 0))
                        self.solved_new_vars_during_this_round = True
            elif largest_n_mines_in_front_alt_solutions + number_of_unclicked_unseen_cells == n_mines_remaining:    # -> every unseen cell must be a mine, see below comment. So: there can be 0 uu_cells. If that's the case, this is true. If there are more than 0 uu_cells, this is STILL true. This is because of the ' + n_uu_cells' here.
                only_max_sum_is_ok = True
                if number_of_unclicked_unseen_cells > 0:
                    for cell in unclicked_unseen_cells:
                        self.minecount_successful = True
                        self.solved_variables.add((cell, 1))                            # if the number of unclicked unseen + max number of mines encountered in any alt solution == currently remaining minecount, then every single cell in unclicked unseen cells must have a mine. I met one such situation in a random game.
                        self.minecount_solved_vars.add((cell, 1))
                        self.solved_new_vars_during_this_round = True
            if self.solved_new_vars_during_this_round:
                self.minecount_successful = True    
                print("✔ FOUND SOLUTIONS FROM EARLY MINECOUNT")                            # it's possibly much faster to return already at this point. During the next round, you can solve more possibly much faster thanks to the new solutions
                return
            if (largest_n_mines_in_front_alt_solutions < n_mines_remaining) and not only_max_sum_is_ok:
                print("GUESSING, no help for minecount")
                choose_best_guess(naive_safest_guess = best_guess, 
                    min_n_mines_in_front = smallest_n_mines_in_front_alt_solutions, best_front_chance = survival_chance)
                return
            print("Minecount filtering of alt solutions is needed")

            if only_min_sum_is_ok:
                value_counts_for_each_var = count_front_sums_to_get_ok_set_alts(only_min_ok = True)
            elif only_max_sum_is_ok:
                value_counts_for_each_var = count_front_sums_to_get_ok_set_alts(only_max_ok = True)
            else:
                value_counts_for_each_var = count_front_sums_to_get_ok_set_alts()                                   # what I need; for every separated set, a list of alts that are ok regarding minecount. From those, just record every variable: is it this time 0 or 1? Count the times of 0 and 1 per variable, and that's it. That is enough info to either solve it OR to make the best possible guess, if a guess is necessary after all this.

            handle_minecount_results(value_counts_for_each_var, 
                smallest_n_mines_in_front_alt_solutions)

        def remove_empty_sets(eq_set_possible_solutions):
            nonempty_eq_set_possible_solutions = []
            for eq_set in eq_set_possible_solutions:
                if len(eq_set[0]) != 0:
                    nonempty_eq_set_possible_solutions.append(eq_set)
            return nonempty_eq_set_possible_solutions

        # This function is PER ONE eq_set instead of the old one, which built solutions and their sums for ALL sets
        def count_mines_of_set_alt_solutions_for_minecount_check(eq_set_alt_solutions:list) -> tuple:   # separated sets = erilliset joukot; here it means that the solution sets do not share a single variable. These separated sets consist of all eligible alt answers per each set. If the sum of a given combination whole-front-alt-answer that's joined together here and which has one alt from each set per combo disagrees with remaining minecount later, it is impossible; discard all such whole-front alt answers. Whether that disagreement happens is found out only by summing the thus-far separated alt answer sets together - that's why I'm combining them here!
            '''
            returns: tuple (nMines_to_setAltSolutions, min_minecount, max_minecount). 
            The 1. one is a ditionary with 
            { number of mines in the alt solution to this set : [alt solution to this set #1, alt solution to this set #2, ...], .... }. This contains ALL the alt solutions to this set! It's just divided by number of mines. That will come in handy later, when inspecting the whole-front alt answers regarding minecount; this makes it a lot faster to discard bad answers before the actual 'construction' even begins.
            The 2. one is the min number of mines that was found in any of the alt solutions to this set. This is needed for minecount.
            The 3. one is the max number of mines that was found in any of the alt solutions to this set. Likewise, for minecount.
            '''
            # needed; for each alt build, I need the sum of the build. I have one or more alt_solutions per each equation, and one or more equations per this set-in-question.
            def count_mines(alt_solution):
                mines = 0
                for var, value in alt_solution.items():
                    mines += value
                return mines

            # needed: (1) build the solution by choosing all alt combinations PER this set-in-question, (2) count the sum for each build
            def handle_alt_solution(set_alt_solution:list, n_mines:int, min_minecount, max_minecount) -> None:
                if n_mines < min_minecount:
                    min_minecount = n_mines
                if n_mines > max_minecount:
                    max_minecount = n_mines
                if n_mines not in nMines_to_setAltSolutions:
                    nMines_to_setAltSolutions[n_mines] = []
                nMines_to_setAltSolutions[n_mines].append(set_alt_solution)
                return min_minecount, max_minecount

            # I also need this. I could just return: (nMines_to_setAltSolutions, min_minecount, max_minecount). That would do it!
            max_minecount = 0
            min_minecount = float('inf')
            nMines_to_setAltSolutions = dict()                      # {number of mines : alt entire-front combined solutions with that number of mines}. Every alt solution from every separate equation set is coupled with every alt solution from every other set, to be able to construct all the possible entire-front alt solutions, the mines of which are counted - this is for being able to use remaining mine count for deducing which of these alt whole-front solutions are impossible. For each of these entire-front alt solutions, discard the impossible ones, then see if the remaining ones all agree regarding one or more variable just like previously, once again using 'handle_possible_whole_solutions()' since it's awesome c:
            for set_alt_solution in eq_set_alt_solutions:           # for in the FIRST equation; this is the starting point for building the entire-front alt solutions (one set alt solution from every set must be chosen)
                min_minecount, max_minecount = handle_alt_solution(set_alt_solution, 
                    count_mines(set_alt_solution), min_minecount, max_minecount)
            return nMines_to_setAltSolutions, min_minecount, max_minecount

        # (5) minecount: for each ENTIRELY COUPLED alt whole solution, get the max and min n_mines. Then send the sets for minecount check and (1) guessing if minecount is not useful (2) minecount if minecount IS useful (3) if minecount still doesn't provide solutions, guess. So guessing can happen before or after the actual 'minecount'
        def count_set_alt_mines_and_send_for_minecount_check(eqSetPossibleSolutions_bestGuess_survivalChance : list) -> None: # list of tuples; each member of the list is for one separated eq set. Each of these tuples is therefore for one eq set: (possibleSolutions, bestGuess, survivalChance if that guess is taken). This is used, if minecount is NOT needed = if minecount canNOT reveal new logic! It's extremely important not to do minecount if not needed, as its machinery is very heavy if the remaining front is big, in worst scenarios.
            print('check_minecount_need() as no solutions were found yet')

            # all these three below are about THE WHOLE front solution; solutions for the WHOLE FRONT, everything seen by 'self.front' in 'botGame.py', everything in yellow when you highlight it in the minesweeper botGame by pressing 'f'. Please try it! c:
            smallest_n_mines_in_front_alt_solutions = largest_n_mines_in_front_alt_solutions = 0

            # consists of triples: (nMines:altSolutions of this set with nMines, Minmines for the whole set, Maxmines for the whole set), for each eq set alt solution. This info is needed in minecount solving later.
            nMinesToAltSolutions_minmines_maxmines_for_each_set = []
            eqSetPossibleSolutions_bestGuess_survivalChance = remove_empty_sets(eqSetPossibleSolutions_bestGuess_survivalChance)
            for eq_set, bestGuess, survivalChance in eqSetPossibleSolutions_bestGuess_survivalChance:
                result = count_mines_of_set_alt_solutions_for_minecount_check(eq_set)
                nMines_to_setAltSolutions, min_minecount, max_minecount = result
                largest_n_mines_in_front_alt_solutions += max_minecount
                smallest_n_mines_in_front_alt_solutions += min_minecount
                nMinesToAltSolutions_minmines_maxmines_for_each_set.append(result)
            check_minecount_need_and_guess_or_minecount(nMinesToAltSolutions_minmines_maxmines_for_each_set,               # get all possible minecount sums; one for each combination of set alt solutions (one alt per separate eq set). Then inspect each corresponding solution using the machinery below, as it works (it's been tested meticulously before already)
                smallest_n_mines_in_front_alt_solutions, largest_n_mines_in_front_alt_solutions,
                bestGuess, survivalChance)  # these two are used in case minecount is NOT needed c: - if minecount is not needed, in English, it provides no useful information, then a GUESS is necessary.

        def handle_flag_box() -> None:
            print('handle_flag_box()')
            if len(all_unclicked) > 0:
                if n_mines_remaining == 0:
                    for cell in all_unclicked:
                        print('- marking var as 0')
                        self.solved_variables.add((cell, 0))
                else:
                    # Both of these below work. The non-commented one is a lot more straightforward, though, and saves work.
                    for uc in all_unclicked:
                        self.guess = uc                                                             # 'all unclicked' is a set(); therefore, to pick the first element, you can't use index - instead do this. In this situation, you have to guess, as the contents of the 'flag box' are a mystery
                    print('- self.guess:', uc)
                    # self.unique_equations = { (tuple(var for var in all_unclicked), minecount)}   # There's a chance for 'self.front' not existing in a case where the game is not finished, i.e. there are non-mine cells in that flag box
                return
            else:
                return                                                                              # btw in minesweeper, this means the game is finished. Actually: the code will NEVER go here, but it's good to put this here just in case this class is used for something else than minesweeper.
        
        def perform_solving() -> None:
            ''' 
            returns nothing: saves solved variables to 'self.solved_variables', etc, as attributes, which can then be used by 'botGame.py' conveniently 
            Guesses only, if no solutions were found using logic
            (0-6) as described in docstring of 'absolut_brut()' 
            '''
            
            # (0) reset variables
            self.reset_variables_before_new_round_of_csp_solving()

            # (0.1) check for a rare situation which I'm calling a 'flag box', where 'self.front' of 'botGame.py' has been emptied, hence there are no 'self.unique_equations' here, and there's a wall of flags preventing seeing to the other side at all. See more explanation in the function 'handle_flag_box()'. I ran into this flag box after around 650 expert games. Yes, I manually pushed 'b' and 'p' for 650 expert games c: yes, I need help
            if not self.unique_equations:                                                               # if there is no 'self.front' at all, there are no 'self.unique_equations' fed into this 'CSP_solver.py' from 'botGame.py'; this can happen when a 'flag box' / 'flag shield' is born in the game, in very rare situations (I just came up with that word, btw) but everything around it has been solved, so that the inner, unseen contents of the flag box are a complete mystery. If that mystery has at least one unclicked cell without a mine, we have to guess somewhere in the box. If the box had only mines, the game would be complete, and nothing would need to be done!
                handle_flag_box()
                return

            # (1.1) (1.2) find separate equation sets; this reduces time complexity in all solution-finding steps later, including in minecount and in guessing, if the sets are NOT assembled together again later!
            setN_to_vars = divide_vars_to_disconnected_sets()
            separate_sets_of_eqs = build_separate_sets_of_equations_from_separate_sets_of_vars(setN_to_vars)

            # (2) get alternative solutions per equation
            alternative_answers_per_equation_per_set_of_eqs = find_and_group_possible_answers_per_single_equation(separate_sets_of_eqs)    # each group represents the answers for a single equation derived from a single number cell on the minesweeper map.

            # (3) chain link equations; overlap of equations via common variables is ensured by (1) performing chain linking for each separated eq set, (2) sorting the equations within each equation set before linking, then linking in the sorting order -> usually max number of variables are shared. NB! For all those variables that are in only one equation, they will later have 'traverse()' count 0 (I guess?)
            compGroups_and_startingGroup = chain_link_equations(alternative_answers_per_equation_per_set_of_eqs)

            # (4) get possible solutions per equation set, and for each equation set, get the best cell to guess (that which has greatest proportion of 0s to 1s in all the possible eq set answers with that variable).
            eq_set_possible_solutions_and_guessing_info_in_case_minecount_is_not_needed = []                                                                                                  # eg. this could be[{a:1,b:0}, {a:0,b:1}] for a situation where there's one fifty-fifty ending, AND in addition an x number of unclicked unseen cells. If the minecount is 1, then all the unclicked unseen cells must be zero.
            for compatibility_groups, starting_group in compGroups_and_startingGroup:
                possible_whole_solutions, best_bet, highest_survival_rate_in_front_cells = join_comp_groups_into_solutions(compatibility_groups, starting_group)
                if self.timeout:
                    return
                eq_set_possible_solutions_and_guessing_info_in_case_minecount_is_not_needed.append(
                    (possible_whole_solutions, best_bet, highest_survival_rate_in_front_cells))

            # (5) use minecount only if necessary. I have reduced time complexity by keeping the eq_sets separated in 'use_minecount' instead of combining them first. That only required summing (and quite complex data structures and loops..).
            if not self.solved_new_vars_during_this_round:                                                                                  # 'self.solved_new_vars_during_this_round' is set to 'True' the very moment that a new variable has been solved, each round of absolut_brut() in two possible situations: in (1) 'handle_possible_whole_solutions()' that was done previously, when any new variable is solved (using normal solving BEFORE minecount, and (2) If non-minecount logic wasn't enough, then I'm using 'use_minecount()' that's called here, and that also marks newly solved variables as True, so that guessing is NOT done. If not solved new, then 'handle_possible_whole_solutions()' is called again, there check for new solutions again, and if still not (3rd attempt, kind of), then guessing is done.
                count_set_alt_mines_and_send_for_minecount_check(eq_set_possible_solutions_and_guessing_info_in_case_minecount_is_not_needed) # (6) if minecount doesn't help, 'use_minecount()' will pick the safest choice for guessing
            else:
                print('- ✔ found solutions, exiting CSP_solver')
        
        perform_solving()

    # NB! This is called, when adding new equations for the first time, AND after finding new variables IF the related equations are (1) new and (2) do not become single solved variables as well (i.e. if the related equations are not reduced from equations like a+b=1 to just solved single variables like b=1). Hence, sometimes the 'self.update_equation(equation)' is necessary.
    def handle_incoming_equations(self, equations:list, reset=True) -> None:                                                            # equations = [(x, y, ((x1, y1), (x2, y2), ...), summa), ...]; so each equation is a tuple of of x, y, unflagged unclicked neighbours (coordinates; unique variables, that is!), and the label of the cell (1,2,...8)
        if reset:
            self.unique_equations = []
            self.variable_to_equations = dict()
        for x,y, variables, summa in equations:                                                                                         # (x,y, variables, sum_of_variables). The x and y are the origin of the equation - actually unnecessary at the moment, I'm not using it for anything atm.
            variables = tuple(sorted(variables))
            self.unique_equations.append((variables, summa))
            for var in variables:
                if var not in self.variable_to_equations:
                    self.variable_to_equations[var] = []
                    self.variables.add(var)
                self.variable_to_equations[var].append((variables, summa))     
        pass  

def format_equation_for_csp_solver(x:int, y:int, variables:tuple, surrounding_mine_count:int) -> list:
    # NB! 'variables' has to be a tuple OR something that can be converted to a tuple
    variables = tuple(variables)  # if there's a cell with (x,y) = (4,5) in self.front, then the variable name shall be '(4,5)'. Simple and effective. The constraint for each variable is [0,1], meaning that the solution for each variable has to be 0 or 1.
    input_addition = [x, y, variables, surrounding_mine_count]
    return input_addition


#####################################################################################################################################
#####################################################################################################################################
#####################################################################################################################################

if __name__ == '__main__':

    test_info_dict = {}

    def print_multiple_results(test_info:dict) -> None:
        number_of_tests = len(test_info.keys())
        n_passed = 0
        passed_tests = []
        n_failed = 0
        failed_tests = []
        failed_results = []
        for name, (csp, expected_result) in test_info.items():
            name, result, actual_result = print_solved_variables(csp, name, expected_result)
            if result == 'passed':
                n_passed += 1
                passed_tests.append(name)
            else:
                n_failed += 1
                failed_tests.append(name)
                failed_results.append(actual_result)
        if n_failed != 0:
            print(f'''
TOTAL:
tests      {number_of_tests} 
passed     {n_passed}
failed     {n_failed}
FAILED tests:''')        
            for i in range(len(failed_tests)):
                print(f'{failed_tests[i]}, instead got: {failed_results[i]}')
        else:
            print("\nALL TESTS PASSED!")

    
    def print_solved_variables(csp:CSP_solver, name='random test', expected_result='') -> None:
        print(f'\nSolving "{name}"')
        concat = 'NOTHING'
        if len(csp.solved_variables) >= 1:
            concat = ''
            for variable, value in sorted(csp.solved_variables):
                print("- solved a new variable!", variable , "=", value)
                concat += str(value)
        if concat == expected_result:
            print('test passed!')
            return(name, 'passed', concat)
        elif len(csp.solved_variables) == 0:
            print('- NO SOLVED VARIABLES!')
            return(name, 'failed', concat)
        else:
            print('TEST FAILED')
            return(name, 'failed', concat)


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

    name = 'test 1a: letters. a0, b1, c1, d0, e1 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4])
    csp.absolut_brut()
    # for solved_variable in csp.solved_variables:
    #     print(solved_variable)
# ('d', 0)
# ('a', 0)
# ('e', 1)
# ('c', 1)
# ('b', 1)
    
    
    expected_result = '01101'
    test_info_dict[name] = [csp, expected_result]
    # print_solved_variables(csp, name, expected_result)

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

    name = 'test 1b: (x,y): (0,0)=0, (0,1)=1, (1,0)=1, (2,0)=0, (3,0)=1 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4])
    csp.absolut_brut()
    
    expected_result = '01101'
    test_info_dict[name] = [csp, expected_result]

    # print_solved_variables(csp, name, expected_result)

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
    expected a=0, b=1, d=0, e=1
    '''
    eq1 = [0, 1, ('a', 'b'), 1]
    eq2 = [1, 1, ('a', 'd'), 0]
    eq3 = [2, 1, ('d', 'e'), 1]
    eq4 = [3, 1, ('d', 'e'), 1]

    name = 'test 1c: letters. a0, b1, d0, e1 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4])
    csp.absolut_brut() 

    
    expected_result = '0101'
    test_info_dict[name] = [csp, expected_result]        
                     
    # print_solved_variables(csp, name, expected_result)

    ############################## Test 2, letters #############################################
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

    name = 'test 2, letters. a0,b1,c0,d1,e0 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4])
    csp.absolut_brut() 

    
    expected_result = '01010'
    test_info_dict[name] = [csp, expected_result]                         
    # print_solved_variables(csp, name, expected_result)

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

    name = 'test 3a, letters. a0,b1,c0,f1 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4])
    csp.absolut_brut()

    
    expected_result = '0101'
    test_info_dict[name] = [csp, expected_result]

    # print_solved_variables(csp, name, expected_result)

    '''correct result: a0,b1,c0,f1 (AND d = not e). This requires the constraints that each is 0 or 1 (to solve b+f=2 -> b=f=1)
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
    
    name = 'test 3b, (x,y). (0,2)=0, (1,2)=1, (2,2)=0, (3,2)=1 (AND (3,0) = not (3,1))'
    csp = CSP_solver()
    csp.handle_incoming_equations([c01, c11, c20, c21])
    csp.absolut_brut()

    
    expected_result = '0101'
    test_info_dict[name] = [csp, expected_result]

    # print_solved_variables(csp, name, expected_result)

    ############################ Test 4a: letters ############################################
    
    eqi     = [3, 1, ('b', 'c'), 1]                         
    eqiii   = [3, 3, ('a', 'b', 'c', 'd', 'e'), 2]
    eqv     = [2, 4, ('a', 'f'), 1]
    eqvi    = [3, 4, ('a', 'd', 'e', 'f', 'g'), 2]
    eqa     = [2, 7, ('h', 'i'), 1]
    eqb     = [3, 5, ('e', 'f', 'g', 'h', 'i'), 2]
    
    name = 'test 4a, letters. e=0 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eqi, eqiii, eqv, eqvi, eqa, eqb])
    csp.absolut_brut()                                  # NB! after 3 rounds minimum, e=0 is solved! A smaller number of rounds is not enough. This is ok and expected given the functions written in the class, as not everything is recursively updated until the end of the world (as this would complicate things even more!); also, nb! The purpose is not to be able to solve everything in one go, as that would also mean that pressing 'b' once in 'botGame.py' would proceed a huge number of steps at a time, AND this has nothing to do, as such, with efficiency either; so I want to divide this into small(ish) steps whenever possible, facilitating visualization and debugging that way, as there's no real reason not to do this. In fact, efficiency-wise, it's better to run as little as CSP_solver as possible, instead relying on the much simpler 'simple_solver' in 'botGame.py' as possible

    expected_result = '0'
    test_info_dict[name] = [csp, expected_result]

    # print_solved_variables(csp, name, expected_result)

    ########################## Test 5a: letters. Based on 'Esim_expert_1.png', which wasn't solved by pressing 'b' (i.e., this test is for actual debugging) #
    
    eq1     = [-1, -1, ('a', 'b'), 1]                         
    eq2     = [-1, -1, ('a', 'b', 'c', 'd', 'e'), 2]
    eq3     = [-1, -1, ('d', 'e', 'f'), 2]
    eq4     = [-1, -1, ('e', 'f', 'g'), 2]
    eq5     = [-1, -1, ('f', 'g', 'h', 'i', 'j'), 1]
    
    name = 'test 5a, letters. c0, d0, e1, f1, g0, h0, i0, j0 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4, eq5])
    csp.absolut_brut()                                  # NB! This needs 2 rounds!

    expected_result = '00110000'
    test_info_dict[name] = [csp, expected_result]


    ########################## Test 6a: letters. Minecount! Make a situation where there's one number cell '1' pointing to two adjacent cells, a and b, and there's also a third cell 'c' that's not seen by any number cell, called 'unclicked unseen' cell; it's boxed by flags so it's not adjacent to 'self.front'! I just ran into a situation like this and the minecount didn't thus work back then; so this is a test that was made for real-case debugging #########

    eq1     = [-1, -1, ('a', 'b'), 1]                         

    name = 'test 6a, letters, MINECOUNT=1. c=0 expected.'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1])
    csp.absolut_brut(n_mines_remaining=1, all_unclicked=['a','b','c'], number_of_unclicked_unseen_cells=1,
        unclicked_unseen_cells=['c'])                 # So, here 'a' and 'b' are seen by number cell that says '1'. So, a+b=1. But also, there's an isolated cell c in the corner, surrounded by three flags, hence not seen by any number cell. The wanted result here is that c=0, because the remaining minecount is 1, and a+b=1, so c=0.

    expected_result = '0'                                                                               # c=0
    test_info_dict[name] = [csp, expected_result]
    

    ########################## Test 7a: letters. NOTHING expected. Minecount (3 mines remaining), minecount not provided to 'absolut_brut()'. Expected: nothing. In the next example, you'll see that even minecount doesn't solve it (see 'Testaus/Esimerkkitilanteita/Test 7b unsolvable even with minecount.pdf' for this case) ##########

    eq1     = [-1, -1, ('a', 'b', 'c'), 1]
    eq2     = [-1, -1, ('b', 'd'), 1]
    eq3     = [-1, -1, ('h', 'i'), 1]
    eq4     = [-1, -1, ('h', 'i'), 1]
    eq5     = [-1, -1, ('d', 'f', 'i', 'j'), 1]                         

    name = 'test 7a, letters. NOTHING expected.'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4, eq5])
    csp.absolut_brut()

    expected_result = 'NOTHING'
    test_info_dict[name] = [csp, expected_result]
    

    ########################## Test 7b: letters. EVEN MINECOUNT DOESN'T SOLVE THIS! Minecount info included, but still unsolvable! So, expected: nothing ############

    eq1     = [-1, -1, ('a', 'b', 'c'), 1]
    eq2     = [-1, -1, ('b', 'd'), 1]
    eq3     = [-1, -1, ('h', 'i'), 1]
    eq4     = [-1, -1, ('h', 'i'), 1]
    eq5     = [-1, -1, ('d', 'f', 'i', 'j'), 1]                         

    name = "Test 7b: MINECOUNT DOESN'T HELP. unsolvable 2. NOTHING expected"
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4, eq5])
    csp.absolut_brut(n_mines_remaining=3, all_unclicked='a b c d e f g h i j k'.split(), number_of_unclicked_unseen_cells=3) # NB! Yes, minecount (3) is the same, by coincidence, as 'number_of_unclicked_unseen_cells'.

    expected_result = 'NOTHING'
    test_info_dict[name] = [csp, expected_result]

    ########################## Test 8a: Expert_minecount-solvable_1. c0, d1, e1, f0, g0, i0, j0, t0 expected. [j,i,t] = unclicked unseen ##############################

    eq1     = [-1, -1, ('a', 'b'), 1]
    eq2     = [-1, -1, ('c', 'd'), 1]
    eq3     = [-1, -1, ('e', 'f'), 1]
    eq4     = [-1, -1, ('d', 'g'), 1]   
    eq5     = [-1, -1, ('k', 'l', 'm'), 1]
    eq6     = [-1, -1, ('l', 'm', 'n'), 1]
    eq7     = [-1, -1, ('m', 'n', 'o'), 1]
    eq8     = [-1, -1, ('n', 'o', 'p'), 1]
    eq9     = [-1, -1, ('o', 'p', 'q'), 1]
    eq10    = [-1, -1, ('p', 'q', 'r'), 1]
    eq11    = [-1, -1, ('e', 'h', 'q', 'r', 's'), 2]

    name = 'Test 8a: Expert_minecount-solvable_1. c0, d1, e1, f0, g0, i0, j0, t0 expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8, eq9, eq10, eq11])
    csp.absolut_brut(n_mines_remaining=6, all_unclicked='a b c d e f g h i j k l m n o p q r s t'.split(), 
        number_of_unclicked_unseen_cells=3, unclicked_unseen_cells=['j', 'i', 't'])

    expected_result = '000' # this was changed after I added an early return from minecount in situations, where the simplest minecount cases already provided answers. This most likely saves a lot of work, cancellign the rest of the minecount machinery which is the heaviest part of minecount (it's then postponed to the next round, if still needed then). So now it can now only solve three variables on the FIRST round. It would take another round to solve the rest, and most likely, could use faster logic for that!
    test_info_dict[name] = [csp, expected_result]

    ########################## Test 9a: Flag box; a=0 expected. An ultra-rare situation where 'self.front' is empty, but there are still non-mine cells inside the flag box ##############################

    name = 'Test 9a: Flag box; a=0 expected. An ultra-rare situation where "self.front" is empty, but there are still non-mine cells inside the flag box'
    csp = CSP_solver()
    # NO EQUATIONS in this test. Yes, this can happen, when a 'flag box' is born in a rare game. If only one side of the box is seen by 'self.front', then the other side is inaccessible without guessing, AND there is no 'self.front' anymore, if everything else has been solved and/or guessed already.
    csp.handle_incoming_equations([]) # no equations, BUT in minesweeper, this function has been called (many many times) before arriving in this 'flag box' situation
    csp.absolut_brut(n_mines_remaining=0, all_unclicked='a'.split(), number_of_unclicked_unseen_cells=1)

    expected_result = '0'
    test_info_dict[name] = [csp, expected_result]

    ########################## Test 9b: Flag box b; nothing expected. An ultra-rare situation where 'self.front' is empty, but there are still non-mine cells inside the flag box. Here, there's one non-mine cell, and one mine cell -> only a guess can be made. This test doesn't check, if the guess is made, however. ##############################

    expected_result = 'NOTHING'

    name = f'Test 9b: Flag box; "{expected_result}" expected. An ultra-rare situation where "self.front" is empty, but there are still non-mine cells inside the flag box'
    csp = CSP_solver()
    # NO EQUATIONS in this test. Yes, this can happen, when a 'flag box' is born in a rare game. If only one side of the box is seen by 'self.front', then the other side is inaccessible without guessing, AND there is no 'self.front' anymore, if everything else has been solved and/or guessed already.
    csp.handle_incoming_equations([]) # no equations, BUT in minesweeper, this function has been called (many many times) before arriving in this 'flag box' situation
    csp.absolut_brut(n_mines_remaining=1, all_unclicked='a b'.split(), number_of_unclicked_unseen_cells=2, 
        unclicked_unseen_cells='a b'.split())
    
    test_info_dict[name] = [csp, expected_result]

    # ######################### Test 8c: minecount helps, complex. ? expected. 0 unseen cells. ##############################

    # eq1     = [-1, -1, ('a', 'b' 'c', 'd', 'e'), 2]
    # eq2     = [-1, -1, ('d', 'e', 'f'), 1]
    # eq3     = [-1, -1, ('e', 'f', 'g'), 1]
    # eq4     = [-1, -1, ('g', 'h'), 1]   
    # eq5     = [-1, -1, ('c', 'd', 'i', 'm'), 3]
    # eq6     = [-1, -1, ('f', 'g', 'h', 'k', 'l', 'n', 'o', 'p'), 4]
    # eq7     = [-1, -1, ('h', 'l', 'p'), 2]
    # eq8     = [-1, -1, ('i', 'm', 'q', 'r'), 2]
    # eq9     = [-1, -1, ('i', 'j', 'k', 'm', 'n', 'r', 's'), 3]
    # eq10    = [-1, -1, ('l', 'p', 't'), 2]
    # eq11    = [-1, -1, ('m', 'n', 'r', 's', 'v', 'w', 'x'), 4]
    # eq12    = [-1, -1, ('n', 'o', 'p', 's', 't', 'x', 'y', 'z'), 4]
    # eq13    = [-1, -1, ('p', 't', 'z', 'a1'), 2]
    # eq14    = [-1, -1, ('t', 'z', 'a1', 'a6', 'a7', 'a8'), 1]
    # eq15    = [-1, -1, ('a2', 'a9'), 1]
    # eq16    = [-1, -1, ('u', 'v', 'a3'), 2]
    # eq17    = [-1, -1, ('w', 'x', 'y', 'a4', 'a5'), 1]
    # eq18    = [-1, -1, ('a2', 'a9'), 1]

    # name = 'Test 8c: solvable only with minecount, complex. ??? expected. 0 unseen cells.'
    # csp = CSP_solver()
    # csp.handle_incoming_equations([eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8, eq9, eq10, eq11, eq12, eq13, eq14, eq15, eq16, eq17, eq18])
    # csp.absolut_brut(minecount=13, all_unclicked='a b c d e f g h i j k l m n o p q r s t u v w x y z a1 a2 a3 a4 a5 a6 a7 a8 a9'.split(), number_of_unclicked_unseen_cells=0)

    # expected_result = '??? dunno'
    # test_info_dict[name] = [csp, expected_result]
    
    print_multiple_results(test_info_dict)


'''
This class is exclusively for MinesweeperBot's botGame; hence, all equations are 1st order, and of the type 

    q*a + w*b + e*c +... = k

where all factors and variables ∈ N and k ∈[0,8] (NB: the original 'raw' equations fed into the 'CSP_solver' will never evaluate to less than 1; there would be nothing to solve in those kinds of equations, as the automatic answer would be 0 for all terms, as each term has to be 0 or 1)

In fact, all raw equations that come straight from the minesweeper map have factors (q,w,e above) = 1, because there is one of each neighbour for each cell.

All the operations I need for handling these equations are (1) subtraction between these linear equations and (2) the inspection of constraint that each cell ∈ {0,1}. This is done by checking if for example ...+2x+... = 1, where the only possible solution for x is x=0, since if x was 1, others would have to be negative, or if a+b+c+... = 0, which means that all terms are 0. This latter one (all 0) can happen only after initial processing, as (like mentioned above), no such equations come 'raw' from the map.
'''