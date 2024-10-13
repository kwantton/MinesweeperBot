'''to-do:
- smart minecount: for all the total alt solutions, subtract them from the total minecount and/or see if the min sum of mines is too high regarding minecount?
- even faster?
- more tests, also on 'botGame.py' side
'''
from itertools import combinations

class CSP_solver:
    def __init__(self, mines_total = float("inf")):

        self.guess = None                                               # 12.10.24: for guessing. If (1) normal solving doesn't help AND (2) mine counting doesn't help either, THEN guess the safest cell. This info, 'self.guess', is passed on to 'botGame.py' where the guess is made. I made a separate variable for this to be able to recognize this guessing situation in 'botGame.py' to distinguish it from normal solving; this makes it possible to add visuals, etc...
        self.choice = None                                              # either 'FRONT' or 'UNSEEN'; is the next guess located next to 'self.front' (botGame.py has 'self.front') or in the cells unseen by self.front? This is for choice of guessing, and for passing this info to 'botGame.py' after the choice has been made.
        self.variables = set()                                          # ALL variables, solved or not
        self.p_success_front = None                                     # initialize. Otherwise 'draw' section in 'pyGame.py' complains that there's no such attribute
        self.p_success_unseen = None                                    # initialize
        self.unique_equations = set()                                   # { ((var1, var2, ..), sum_of_mines_in_vars), (...) }. Each var (variable) has format (x,y) of that cell's location; cell with a number label 1...8 = var. Here, I want uniqe EQUATIONS, not unique LOCATIONS, and therefore origin-(x,y) is not stored here. It's possible to get the same equation for example from two different sides, and via multiple different calculation routes, and it's of course possible to mistakenly try to add the same equation multiple times; that's another reason to use a set() here, the main reason being fast search from this hashed set.        
        self.solved_variables = set()                                   # ((x,y), value); the name of the variable is (x,y) where x and y are its location in the minesweeper map (if applicable), and the value of the variable is either 0 or 1, if everything is ok (each variable is one cell in the minesweeper map, and its value is the number of mines in the cell; 0 or 1, that is)
        self.mines_total = mines_total
        self.previous_round_minecount = -1                              # if this stays the same for 2 rounds, then use minecount
        self.minecount_successful = False
        self.impossible_combinations = set()

    def reset_variables(self):
        self.guess = None                                               # resetting this to 'None' at the start of every round of 'absolut_brut()', in case the previous round was a guess. (12.10.2024): this is the default value. If even mine counting doesn't help, then this is set to True in 'handle_possible_whole_solutions()'. That info is then read in 'botGame.py' to handle the guessing.
        self.choice = None                                                      
        self.p_success_front = None                                             
        self.p_success_unseen = None                                            
        self.minecount_successful = False

    # 100% solution: (1) PER EACH EQUATION that MUST be satisfied (i.e. each number cell on the minesweeper map), try all combinations of ones (=mines). That's what THIS function does. (2) After this function below, from all of the alternative combinations of 1s and 0s that DO satisfy the CURRENT equation, find those alternatives that are incompatible with all other equations, pairing one group's all possible alts with compatible alts of ONE other group (i.e. "groups", i.e. incompatible with ALL the alternative solutions of at least one other group) (3) from the remaining alt equations per group (i.e. PER original equation), find columns where a variable is always 0 or 1 -> it HAS to be 0 or 1 ALWAYS. Then see these new solutions, inspect the remaining equations for untrue alternatives now that we've solved a new variable (or many new variables), and keep repeating the whole loop (1),(2),(3) as long as new solutions keep coming. Stop iteration when there are no longer new solutions produced by the whole loop.
    def absolut_brut(self, minecount=-1, need_for_minecount = False, all_unclicked = [], number_of_unclicked_unseen_cells=-1) -> None:   # minecounting logic is used ONLY if the minecount is not changing, i.e., if CSP_solver is currently incapable of solving any more of the map without minecount (not enough information -> 'normal' logic is not enough). In this situation, use information that unclicked_cell_1 + unclicked_cell_2 + unclicked_cell_3 + .... = total number of mines remaining in the entire map (HOWEVER! that equation is not used; it would be too slow, extremely slow at large numbers of unclicked cells remaining). In some cases, that helps solve the remaining situation, sometimes not.

        self.reset_variables()
        if not self.unique_equations:
            return
        
        # print("minecount from CSP_solver:", minecount)                        # the number of unlocated maps at this point
        # print("previous round minecount:", self.previous_round_minecount)
        
        def handle_minecount():
            print("NEED FOR MINECOUNT")
            print("number_of_unclicked_unseen_cells:", number_of_unclicked_unseen_cells)
            total_eq = (tuple(coord for coord in all_unclicked), minecount)
            # self.handle_incoming_equations([(-1,-1, total_eq[0], total_eq[1])], reset=False)           # OLD. (x, y, variables, sum_of_variables) is the format of every equation that's fed (in a list) to 'self.handle_incoming_equations([eq1, eq2...])'. The x and y don't matter; they are the ORIGIN of the equation (origin, as in, from where on the minesweeper map the equation came from). It doesn't affect the result in any way, so I'm using -1, -1 to mark that it's not from a single origin, instead a compound (in this case; all the remaining unclicked cells)
            print('total_eq:', total_eq)
            print('variables in total_eq = len(total_eq[0]):', len(total_eq[0]))
            
        
        if need_for_minecount:
            handle_minecount()
        self.previous_round_minecount = minecount

        # for each separate group of eqs, for each equation (i.e. each number cell on the minesweeper map), given that each variable (= each unopened cell) is 0 or 1 (no mine or a mine), find all possible combinations of 1s and 0s that can satisfy that SINGLE equation GIVEN THAT it has sum = k (some integer number = the number of mines in those unopened surrounding cells in total!)
        def find_and_group_possible_answers_per_single_equation(groups_of_eqs:list) -> list:
            alt_answers_for_groups = list()
            for group_of_eqs in groups_of_eqs:
                alt_answers_per_equation = []
                for variables, summa in group_of_eqs:
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

        # used in 'restrict_solution_space_as_equation_pairs_with_common_variables()' below; are there common variables between two equations (i.e. groups)?
        def common_vars(vars1, vars2) -> bool:
            common = False
            varsB = set(twople[0] for twople in vars2)                              # twople = (var, value), but obviously I can't name it 'tuple' since that's reserved in Python
            for twople in vars1:
                if twople[0] in varsB:
                    common = True
                    break
            return common
        
        def find_equation_groups() -> dict:                                         # FINDS SEPARATE EQUATION GROUPS; finds separate groups of equations that do not share a single variable between the equation groups. For example a+b = 1 and b+c=1 would be one group, separate from e+f+g=2, if there was only those three equations in total in self.unique_equations.
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
                    if (vars, summa) not in completely_grouped_eqs:
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
     
        groupN_to_vars = find_equation_groups()
        separate_groups_of_vars = [group for group in groupN_to_vars.values()]      # in the first 8 tests, there's just one 'separate' group, meaning that all the variables are connected. In real minesweeper, especially in expert, you frequently see more than one separate group, meaning that one's mine locations do not directly affect the other's logic in any way.
        if len(separate_groups_of_vars) == 1:
            separate_groups_of_eqs = [self.unique_equations]                        # just to demonstrate (the same thing would happen in the 'else' below): if all the unique equations are in one connected group, then that's that. Otherwise, get all equations for all groups.
        else:
            separate_groups_of_eqs = []
            for group_of_vars in separate_groups_of_vars:
                eqs_of_this_group = set()
                for var in group_of_vars:
                    eqs_for_var = self.variable_to_equations[var]
                    for eq in eqs_for_var:
                        eqs_of_this_group.add(eq)
                separate_groups_of_eqs.append(eqs_of_this_group)

        alternative_answers_per_equation_per_set_of_eqs = find_and_group_possible_answers_per_single_equation(separate_groups_of_eqs)    # each group represents the answers for a single equation derived from a single number cell on the minesweeper map.
        

        # for each separated set (set=joukko) of equations, do the following: for each group (group=alternative solutions for ONE equation like a+b=1 ('a' is a cell on the minesweeper map, 'b' is another cell)), find at least one solution that's compatible with AT LEAST ONE alternative solution from EXACTLY ONE other group. Then for those compatible alt solutions, couple all of those to the NEXT group (i.e. to the next equation); this builds a chain of equations, where all neighbouring alt solutions are compatible, where the first equation is linked to one equation, the next one to the previous and to the next, etc, and the last one is linked only to the previous one. AFTER 'chain_link_equations', continue to build all possible alternative answers from those, so that there's bookkeeping for every variable for every possible unique alt whole-solution, so that if a conflict is found, building of that alt solution tree is terminated on the spot -> less computation wasted c:
        def chain_link_equations(alternative_answers_per_equation_per_set_of_eqs:list) -> dict:
            comp_groups_and_starting_groups = []
            for alternative_answers_per_eq in alternative_answers_per_equation_per_set_of_eqs:
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
                                for var1, val1 in altA:                         # e.g. 'a', 0. Each var1, val1 has to be compatible with at least ONE alt2 from every other group, so that 'altA_is_viable'!
                                    opposite_value = (var1, int(not val1))      # val1 = 1 or 0; if 1, opposite = (var1, 0). This is so I can avoid if-clause below, making it shorter.
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

        compGroups_and_startingGroup = chain_link_equations(alternative_answers_per_equation_per_set_of_eqs)
        for compatibility_groups, starting_group in compGroups_and_startingGroup:
            if compatibility_groups == 'stop':                                  # commented out above, pay no attention to this 'stop' here
                return                                                          # the idea here is: if simple solutions were found above, use them first (i.e. just return, stop), don't use the heavier tree building below if not necessary

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
               
        def handle_possible_whole_solutions(possible_whole_solutions : list, min_n_mines_in_front = 0, called_from_minecount = False):
            '''
            parameters: 
                possible_whole_solutions    : list of dictionaries, each dict is {var1 : value1, ...}
                min_n_mines_in_front        : int. The minimum number of mines in 'self.front' in 'botGame.py'
                called_from_minecount       : bool. If called from minecount, and no solutions are found, then guess (probe) the safest possible cell on the map.
            '''
            final_answers = dict()
            n_alts = len(possible_whole_solutions)                              # number of alternative total answers. I need this for probability calculation
            if n_alts == 0:                                                     # since I'm dividing by 'n_alts' below, I'm making sure no division by 0 is happening ever.
                return
            counts_of_0 = dict()                                                # needed for guessing; let's find the most safe guess
            most_zeros = 0
            best_chance = 0                                                     # percent P(cell is not a mine). We want the max value here, and the winner is the cell that's going to be guessed
            new_answer_count = 0
            naive_safest_guess = None
            for dictionary in possible_whole_solutions:
                for var, val in dictionary.items():
                    if var not in counts_of_0:
                        counts_of_0[var] = 0
                    if val == 0:
                        counts_of_0[var] += 1
                        if counts_of_0[var] > most_zeros:
                            most_zeros = counts_of_0[var]
                            best_chance = 100*counts_of_0[var]/n_alts           # percent: in how many alt solutions is this cell not a mine, divided by the total number of alt solutions
                            naive_safest_guess = var                            # why 'naive'? Because there are guesses which, even if they prove not to be a mine after guessing, tell NOTHING new about the resulting situation; NOTHING useful based on which the NEXT move could be made. This means not only is also the NEXT move a guess, but ALSO it's less safe than the 'safest' guess taken during this round as the remaining mine density is now higher in the remaining unclicked cells; i.e., it's possible, that the naive 'safest' guess during this round is IN REALITY is the LEAST SAFE guess considering also the next round! This is relatively rare, but it's possible. Checking if this worst-case-scenario happens would NOT be simple at all; it would involve checking the resulting situation (better yet, all possible resulting situations!) and determining if all of them / majority of them result in a manageable situation (i.e. no guessing required, OR a relatively safe guess required). I have no existing machinery for that, and constructing such would take a LOT of work.
                            # print('naive_safest_guess:', var)
                    if var not in final_answers:
                        final_answers[var] = val
                        new_answer_count += 1
                    elif final_answers[var] == 'either or':
                        pass                                                    # I need this for accurate 'new_answer_count'
                    elif final_answers[var] != val:
                        final_answers[var] = 'either or'                        # either this was 'either or' was here or not, the result is the same - 'either or'  
                        new_answer_count -= 1
            if new_answer_count != 0:                                            # micro-optimization, skipping the below loop when no solutions were found
                for var, val in final_answers.items():
                    if val != 'either or':
                        self.solved_variables.add((var, val))
                if called_from_minecount:
                    self.minecount_successful = True
            else:
                print('new_answer_count == 0')
                if called_from_minecount:                                       # => GUESS! If (1) normal solving doesn't help AND (2) mine counting doesn't help either, which is checked by the 'if' clause here, THEN guess the safest cell; that cell which had the highest count of 0s in all of the assembled whole solutions. This info, 'self.guess', is passed on to 'botGame.py' where the guess is made. I made a separate variable for this to be able to recognize this guessing situation in 'botGame.py' to distinguish it from normal solving; this makes it possible to add visuals, etc...
                    print('GUESS:')
                    self.guess = naive_safest_guess                             # default. The below might be fals -> the default stays.
                    self.choice = 'FRONT'
                    if number_of_unclicked_unseen_cells > 0:                    # Can't guess unseen cell if there are no unseen unclicked cells.
                        unclicked_unseen_cell_mine_probability_in_worst_scenario = 100-(100 *(minecount - min_n_mines_in_front) / number_of_unclicked_unseen_cells)  # 100 - percent mine density in unclicked unseen cells in the case that there's the minimum possible number of mines remaining in self.front. It's arbitrary that I chose to inspect the worst case scenario, but generally speaking it's better to opt for guessing cells of partially-known situations than random whatever-tiles in many situations, since often guessing near the front has a higher chance of uncovering more logically solvable situations. However, as that depends on pretty much everything, I repeat that this is NOT the optimal solution in many cases!
                        if best_chance < unclicked_unseen_cell_mine_probability_in_worst_scenario:
                            self.guess = "pick unclicked"                           # 12.10.24: for guessing. If 'unclicked' cells have the lowest mine density, then guess there. 
                            self.choice = 'UNSEEN'
                    else:
                        self.guess = naive_safest_guess
                        self.choice = 'FRONT'
                    self.p_success_front = round(best_chance, 1)
                    print('- p_success(front)  =', self.p_success_front, '%')
                    if number_of_unclicked_unseen_cells > 0:
                        self.p_success_unseen = round(unclicked_unseen_cell_mine_probability_in_worst_scenario, 1)
                        print("- p_success(unseen) ≥", self.p_success_unseen, '%')
                    print('- guess:', self.choice)
            pass
        
        def join_comp_groups_into_solutions(compatibility_groups:dict) -> list:     # also return the whole list of 'possible_whole_solutions'; it's needed IF minecount is needed. If minecount is needed
            keyVars_to_keys = keyVars_to_keys_builder(compatibility_groups)
            n_groups = len(keyVars_to_keys.keys())
            possible_whole_solutions = []
            
            def traverse(this_alt, entered_alts_for_this_build, 
                possible_solution_build, already_handled_groups) -> None:

                already_handled_groups_local = already_handled_groups.copy()
                possible_solution_build_local = possible_solution_build.copy()
                entered_alts_for_this_build_local = entered_alts_for_this_build.copy()                
                
                if this_alt in compatibility_groups:                            # If this alt solution is not a key in 'compatibility_groups', then IT IS UNTRUE as it's incompatible with one or more other groups' every possible alt answer; in that case, do NOT handle this alt at all (do not (1) mark its variables' proposed values as possible solutions, and do not (2) mark the group that it presents as handled); if the current alt is NOT present as a key of 'compatibility_groups', IT IS INCOMPATIBLE WITH AT LEAST ONE OTHER GROUP. In English, if the current alt solution is not present as a key in 'compatibility_groups', it CANNOT EVER SATISFY ALL THE EQUATIONS that we know MUST be true using at least one combination of alt solutions.
                    group_of_this_alt = identify_group(this_alt)                # 'this_alt' is an alt answer for some group - 'identify_group(this_alt)' tells me WHICH group it belongs to. I want EXACTLY ONE alt answer for EACH group, as each group represents an original equation from the minesweeper map (a number cell, the equation of which is always true, so MUST be satisfied and MUST be compatible with all other groups!)
                    if group_of_this_alt not in already_handled_groups_local:   # NB! So, I only want EXACTLY ONE alt solution per group. If an alt solution has already been handled, DO NOT HANDLE ANOTHER; that another alt solution will be handled in a whole another iteration of this 'traverse()'. (2) Comparison of sets in python; if the values in the set are the same, then the sets are 'equal' in the == comparison. Nice.

                        incompatible_alt_solution = check_for_disagreements(            # this cannot happen on the FIRST call of 'traverse()', but it CAN happen on subsequent later calls - the 'compatibility_groups' only ensure PAIR compatibility, not beyond than that!
                            this_alt, possible_solution_build_local)
                        if incompatible_alt_solution:                                   # if this alt solution disagrees i.e. is incompatible with already-recorded alt solutions (one from each met group so far), then move on to the next 'proposed_matching_alt' (which may be of the same OR of different group!) NB! Do NOT mark the group of the current alt solution as handled if it's incompatible; this means that we still need to wait for a compatible alt to come by from this group, so I must NOT mark it as handled yet!
                            return

                        # this includes the current alt solution
                        for var, value in this_alt:                         # (('a',0), ('b',1), ...) a 'proposed_matching_alt' has this format. It's one alt solution to an equation that's derived from the minesweeper map and which has to have ONE alt solution, the other ones being untrue.
                            possible_solution_build_local[var] = value           # there can be 1 or 2 per variable. If 2, it means that there is not enough information (yet) for solving this variable. If only 1 value, great, that means the value is now solved.
                        
                        already_handled_groups_local.append(group_of_this_alt)   # Since the alt solution was picked, mark the respective group as handled. ATM this is unnecessary, since I'm traversing through the equations in the same chain order as they were linked earlier, but If I were to change that, then this check is needed (previously, I DID need this, but this is a good check also for debugging anyways!)

                        if n_groups == len(already_handled_groups_local):
                            possible_whole_solutions.append(possible_solution_build_local)
                            return                                          # if it's done, it's done. The possible next matches would be to a completely different group, AND it's not possible to gain more solutions from this one, as new groups and their alts are only ADDED in this 'traverse()', not removed, and we've already been to all groups -> return, don't continue!
                        
                        new_matches = compatibility_groups[this_alt]        # continue to matches of this alt solution ONLY if none of the values of this alt solution disagree with values that have already been recorded in 'possible_solution_build' as values of the variables
                        entered_alts_for_this_build_local.add(this_alt)
                        
                        # only do this if the above has not been fulfilled; it's not possible to gain another answer by trying to add yet another alt solution in the case where all the equations (all groups) have already been satisfied, which is checked in the 'if' clause above. SO: for every set of new_matches, I want the info that was updated according to what happened in the specific alternative solution above; which alt solution ('proposed_matching_alt') was 'entered' (seen, processed), which 'group' (equation) in question was handled. Since all the alternatives in the above loop are indeed ALTERNATIVES, they are NOT all saved immediately! (that would be incorrect), instead that is done after the 'traverse()'s below!
                        if new_matches:
                            for new_match in new_matches:
                                if new_match not in entered_alts_for_this_build_local:    # technically redundant, probably almost no effect regarding computing efficiency, BUT it's nice for clarity, and showing the logic still (even if double check)
                                    traverse(new_match, 
                                        entered_alts_for_this_build_local, possible_solution_build_local, already_handled_groups_local)
                        
            # 'starting_group' is the group from where all arrows leave, and back to which no arrows return; an alt origin for an alt rooted tree, essentially!
            for alt_origin in starting_group:                                       # E.g.: ('d', 'e'), [(('d',1),('e',0)), (('d',0),('e',1))]. This quarantees that they build unidentical solution trees that together encompass all possible whole solutions.
                if alt_origin in compatibility_groups:                              # some might have been filtered out as they were no longer fitting ALL other groups; the whole key has been deleted from 'compatibility_groups' if it's not compatible with ANY alt solution from its paired group (paired equation)
                    seen_proposed_vectors = set()                                   # PER alt answer, of course - that's why it's initialized here and not at the top of this 'join_groups_into_solutions'
                    handled_groups = []
                    alt_solution_build = {}
                    traverse(alt_origin, seen_proposed_vectors, 
                        alt_solution_build, handled_groups)                         # 'traverse' builds alternative 'possible_whole_solutions' and saves all viable ones to 'possible_whole_solutions'
            handle_possible_whole_solutions(possible_whole_solutions)
            return possible_whole_solutions
                
        eq_set_possible_solutions = []  # eg. this could be[{a:1,b:0},{a:0,b:1}] for a situation where there's one fifty-fifty ending, AND in addition an x number of unclicked unseen cells. If the minecount is 1, then all the unclicked unseen cells must be zero.
        for compatibility_groups, starting_group in compGroups_and_startingGroup:
            possible_whole_solutions = join_comp_groups_into_solutions(compatibility_groups)
            eq_set_possible_solutions.append(possible_whole_solutions)
        
        def combine_separated_eq_set_alts_in_all_possible_combinations_and_count_their_sums_for_minecount_check(eq_set_possible_solutions:list) -> dict:   # separated sets = erilliset joukot; here it means that the solution sets do not share a single variable. These separated sets consist of all eligible alt answers per each set. If the sum of a given combination whole-front-alt-answer that's joined together here and which has one alt from each set per combo disagrees with remaining minecount later, it is impossible; discard all such whole-front alt answers. Whether that disagreement happens is found out only by summing the thus-far separated alt answer sets together - that's why I'm combining them here!

            def check_nMines_length(nMines_to_frontAltSolutions) -> str:
                nMines_length = 0
                for key, alts in nMines_to_frontAltSolutions.items():
                    nMines_length += len(alts)
                n_combinations = 1
                for set_alts in filtered_eq_set_alt_solutions:
                    n_combinations *= len(set_alts)
                if n_combinations != nMines_length:
                    return 'INCORRECT'
                return 'CORRECT'
            
            def remove_empty_eq_sets(eq_set_possible_solutions:list) -> list:
                filtered_list = []
                for setti in eq_set_possible_solutions:
                    if len(setti) != 0:
                        filtered_list.append(setti)
                return filtered_list
            
            def sum_of(alt_solution):
                summa = 0
                for var, value in alt_solution.items():
                    summa += value
                return summa
            
            def append_alt_solution(current_build:list, current_summa:int, current_index:int) -> None:
                if current_index < n_sets:
                    for alt_solution in filtered_eq_set_alt_solutions[current_index]:
                        current_build_local = current_build.copy()
                        current_build_local.append(alt_solution)
                        append_alt_solution(current_build_local, current_summa + sum_of(alt_solution), current_index + 1)
                else:
                    if current_summa not in nMines_to_frontAltSolutions:
                        nMines_to_frontAltSolutions[current_summa] = []
                    nMines_to_frontAltSolutions[current_summa].append(current_build)

            filtered_eq_set_alt_solutions = remove_empty_eq_sets(eq_set_possible_solutions)    # get rid of empty eq sets, so it doesn't falsify len() of eq sets below
            n_sets = len(filtered_eq_set_alt_solutions)
            nMines_to_frontAltSolutions = dict()         # {number of mines : alt entire-front combined solutions with that number of mines}. Every alt solution from every separate equation set is coupled with every alt solution from every other set, to be able to construct all the possible entire-front alt solutions, the mines of which are counted - this is for being able to use remaining mine count for deducing which of these alt whole-front solutions are impossible. For each of these entire-front alt solutions, discard the impossible ones, then see if the remaining ones all agree regarding one or more variable just like previously, once again using 'handle_possible_whole_solutions()' since it's awesome c:
            for set_alt_solution in filtered_eq_set_alt_solutions[0]:   # in the FIRST one; this is the starting point for building the entire-front alt solutions (one set alt solution from every set must be chosen)
                append_alt_solution(current_build = [set_alt_solution], current_summa = sum_of(set_alt_solution), current_index = 1)
            if check_nMines_length(nMines_to_frontAltSolutions) == 'INCORRECT':
                raise ValueError('WRONG RESULT IN FUNCTION combine_separated_eq_set_alts_in_all_possible_combinations_and_count_their_sums_for_minecount_check()')
            return nMines_to_frontAltSolutions
        
        # for each ENTIRELY COUPLED alt whole solution
        def use_minecount():
            print('\nuse_minecount() since no solutions were found without it')

            # all these three below are about THE WHOLE front solution; solutions for the WHOLE FRONT, everything seen by 'self.front' in 'botGame.py', everything in yellow when you highlight it in the minesweeper botGame by pressing 'f'. Please try it! c:
            alt_solutions_with_ok_minecount = []
            largest_n_mines_in_front_alt_solutions = 0
            smallest_n_mines_in_front_alt_solutions = self.mines_total
            nMines_to_frontAltSolutions = combine_separated_eq_set_alts_in_all_possible_combinations_and_count_their_sums_for_minecount_check(eq_set_possible_solutions)

            for n_mines, front_alt_solutions in nMines_to_frontAltSolutions.items():
                if n_mines < smallest_n_mines_in_front_alt_solutions:
                    smallest_n_mines_in_front_alt_solutions = n_mines
                if n_mines > largest_n_mines_in_front_alt_solutions:
                    largest_n_mines_in_front_alt_solutions = n_mines
                if n_mines + number_of_unclicked_unseen_cells < minecount:              # Example: 8a. Any alt for which this happens is impossible. The max number of mines in 'unclicked unseen cells' is the number of those cells. So if this alt solution + that is less than the actual remaining minecount, then it's impossible
                    pass
                elif n_mines > minecount:
                    pass                                                                # impossible. For example; Test 8a. So, if 'n_mines' (number of mines in total in the current entire-front alt solution) + the number of unseen unclicked cells (all of which COULD have a mine, in the maximum case) is less than the remaining minecount, then this current alt solution minecount is simply too small -> impossible alt solution.
                else:
                    for alt_solutions_of_this_length in front_alt_solutions:
                        for alt_solution in alt_solutions_of_this_length:
                            alt_solutions_with_ok_minecount.append(alt_solution)        # All the alt solutions here that you see that do NOT sum up to the currently remaining minecount are such that there is also at least the number of 'minecount'-'n_mines' unclicked unseen cells remaining as well. So if here's an alt solution that has 2 mines, but there are 3 mines remaining in the minecount, then there must be at least 1 unclicked unseen cell as well for this alt solution to be ok.
            if number_of_unclicked_unseen_cells > 0:
                if smallest_n_mines_in_front_alt_solutions == minecount:                # if none of the alt solutions have less mines than the currently remaining minecount, then all the unclicked unseen cells, which are NOT a part of any of these alt solutions, must NOT have a mine, otherwise the total minecount would exceed the REAL total minecount!
                    for cell in all_unclicked:
                        if cell not in self.variables:                                  # all cells in 'self.variables' have come through 'handle_incoming_equations', so they are seen by 'self.front'. All other 'unclicked' cells are NOT in 'self.front'.
                            self.solved_variables.add((cell, 0))
                elif largest_n_mines_in_front_alt_solutions + number_of_unclicked_unseen_cells == minecount:    # -> every unseen cell must be a mine, see below comment
                    for cell in all_unclicked:
                        if cell not in self.variables:                                  # if the number of unclicked unseen + max number of mines encountered in any alt solution == currently remaining minecount, then every single cell in unclicked unseen cells must have a mine. I met one such situation in a random game.
                            self.solved_variables.add((cell, 1))
            handle_possible_whole_solutions(alt_solutions_with_ok_minecount, min_n_mines_in_front=smallest_n_mines_in_front_alt_solutions, called_from_minecount=True)

        
        if need_for_minecount:
            use_minecount()
            

        # TO-DO: save the non-complete solution candidates in 'join_comp_groups_into_solutions' 'handle_possible_whole_solutions()', and for each of the possible solutions combined with the other set's solutions, check if the number of currently non-variable-status unclicked cells (theoretically all of them can be 1, i.e., a mine) + the number of mines in the entire alt solution is less than the number of remaining mines -> impossible solution, since too few mines in total! 
        
        def solution_finder_from_compatibility_groups(compatibility_groups:dict) -> dict:
            def key_altSolution_inspector():
                new_solutions = set()
                keyVars_to_keys = keyVars_to_keys_builder(compatibility_groups)
                for keyVars, proposed_values in keyVars_to_keys.items():            # each item in 'keyVars' represents a unique equation from the minesweeper map; so each item in 'keyVars' MUST be satisfied one way or another.
                    if len(proposed_values) == 1:
                        for var, value in proposed_values[0]:
                            if (var, value) not in self.solved_variables:
                                self.solved_variables.add((var,value))
                                new_solutions.add((var,value))                      # I need to know if it ACTUALLY solved something new!
                    else:
                        var_to_possibleValues = dict()                              # for each proposed ((var1,value1), (var2,value2), ...), here called a 'vector', record the value. Since all these vectors now inspected are derived from a single equation that MUST be solved, then if all the suggested values are equal for a variable, it MUST be solved as that value, as otherwise the equation could not be solved. Use debugger if this is unclear, it shows very clearly what's happening here c:
                        for proposed_vector in proposed_values:                     # NB! This gathers all possible values for each variable (i.e., 0, or 1, or 0 and 1 per variable!) for ALL the proposed vectors per key; so
                            for var,value in proposed_vector:
                                if var not in var_to_possibleValues:
                                    var_to_possibleValues[var] = []
                                if value not in var_to_possibleValues[var]:         # I wanted to use a list instead of a set because [can't-remember-why!]. That's why I HAVE to check if the value is already in the list.
                                    var_to_possibleValues[var].append(value)
                        for var,values in var_to_possibleValues.items():
                            if len(values) == 1:
                                if (var, value) not in self.solved_variables:
                                    self.solved_variables.add((var, values[0]))
                                    new_solutions.add((var,values[0]))
                return new_solutions
        # solution_finder_from_compatibility_groups(compatibility_groups)       # works, but I'm not using it.

    # NB! This is called, when adding new equations for the first time, AND after finding new variables IF the related equations are (1) new and (2) do not become single solved variables as well (i.e. if the related equations are not reduced from equations like a+b=1 to just solved single variables like b=1). Hence, sometimes the 'self.update_equation(equation)' is necessary.
    def handle_incoming_equations(self, equations:list, reset=True) -> None:    # equations = [(x, y, ((x1, y1), (x2, y2), ...), summa), ...]; so each equation is a tuple of of x, y, unflagged unclicked neighbours (coordinates; unique variables, that is!), and the label of the cell (1,2,...8)
        if reset:
            self.unique_equations = set()
            self.variable_to_equations = dict()
        for x,y, variables, summa in equations:                                 # (x,y, variables, sum_of_variables). The x and y are the origin of the equation - actually unnecessary at the moment, I'm not using it for anything atm.
            variables = tuple(sorted(variables))
            self.unique_equations.add((variables, summa))
            for var in variables:
                if var not in self.variable_to_equations:
                    self.variable_to_equations[var] = set()
                    self.variables.add(var)
                self.variable_to_equations[var].add((variables, summa))     
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
    csp.absolut_brut(minecount=1, need_for_minecount=True, all_unclicked=['a','b','c'], number_of_unclicked_unseen_cells=1)                 # So, here 'a' and 'b' are seen by number cell that says '1'. So, a+b=1. But also, there's an isolated cell c in the corner, surrounded by three flags, hence not seen by any number cell. The wanted result here is that c=0, because the remaining minecount is 1, and a+b=1, so c=0.

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

    name = 'Test 7b: unsolvable 2. NOTHING expected'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1, eq2, eq3, eq4, eq5])
    csp.absolut_brut(minecount=3, need_for_minecount=True, all_unclicked='a b c d e f g h i j k'.split(), number_of_unclicked_unseen_cells=3) # NB! Yes, minecount (3) is the same, by coincidence, as 'number_of_unclicked_unseen_cells'.

    expected_result = 'NOTHING'
    test_info_dict[name] = [csp, expected_result]

    ########################## Test 8a: Expert_minecount-solvable_1. c0, d1, e1, f0, g0, i0, j0, t0 expected ##############################

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
    csp.absolut_brut(minecount=6, need_for_minecount=True, all_unclicked='a b c d e f g h i j k l m n o p q r s t'.split(), number_of_unclicked_unseen_cells=2)

    expected_result = '01100000'
    test_info_dict[name] = [csp, expected_result]

    ########################## Test 8c: minecount helps, complex. ? expected. 0 unseen cells. ##############################

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
    # csp.absolut_brut(minecount=13, need_for_minecount=True, all_unclicked='a b c d e f g h i j k l m n o p q r s t u v w x y z a1 a2 a3 a4 a5 a6 a7 a8 a9'.split(), number_of_unclicked_unseen_cells=0)

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