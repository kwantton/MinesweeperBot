'''to-do:
- make it snappy; now 'botGame.py' is laggy; update data structures as needed, find the cause of the lag
'''
from itertools import combinations

class CSP_solver:
    def __init__(self, mines_total = 100):

        self.variables = set()                                          # ALL variables, solved or not
        self.unique_equations = set()                                   # { ((var1, var2, ..), sum_of_mines_in_vars), (...) }. Each var (variable) has format (x,y) of that cell's location; cell with a number label 1...8 = var. Here, I want uniqe EQUATIONS, not unique LOCATIONS, and therefore origin-(x,y) is not stored here. It's possible to get the same equation for example from two different sides, and via multiple different calculation routes, and it's of course possible to mistakenly try to add the same equation multiple times; that's another reason to use a set() here, the main reason being fast search from this hashed set.        
        self.solved_variables = set()                                   # ((x,y), value); the name of the variable is (x,y) where x and y are its location in the minesweeper map (if applicable), and the value of the variable is either 0 or 1, if everything is ok (each variable is one cell in the minesweeper map, and its value is the number of mines in the cell; 0 or 1, that is)
        self.mines_total = mines_total
        self.previous_round_minecount = -1                              # if this stays the same for 2 rounds, then use minecount
        self.impossible_combinations = set()

    # 100% solution: (1) PER EACH EQUATION that MUST be satisfied (i.e. each number cell on the minesweeper map), try all combinations of ones (=mines). That's what THIS function does. (2) After this function below, from all of the alternative combinations of 1s and 0s that DO satisfy the CURRENT equation, find those alternatives that are incompatible with all other equations, pairing one group's all possible alts with compatible alts of ONE other group (i.e. "groups", i.e. incompatible with ALL the alternative solutions of at least one other group) (3) from the remaining alt equations per group (i.e. PER original equation), find columns where a variable is always 0 or 1 -> it HAS to be 0 or 1 ALWAYS. Then see these new solutions, inspect the remaining equations for untrue alternatives now that we've solved a new variable (or many new variables), and keep repeating the whole loop (1),(2),(3) as long as new solutions keep coming. Stop iteration when there are no longer new solutions produced by the whole loop.
    def absolut_brut(self, minecount=-1, need_for_minecount = False, all_unclicked = []) -> None:   # mineconting logic is used ONLY if the minecount is not changing, i.e., if CSP_solver is currently incapable of solving any more of the map (not enough information -> normal logic is not enough). In this situation, add another equation, which is unclicked_cell_1 + unclicked_cell_2 + unclicked_cell_3 + .... = total number of mines remaining in the entire map. In some cases, that helps solve the remaining situation, sometimes not.

        if not self.unique_equations:
            return
        
        print("minecount from CSP_solver:", minecount)                      # the number of unlocated maps at this point
        print("previous round minecount:", self.previous_round_minecount)
        
        def handle_minecount():
            print("NEED FOR MINECOUNT")
            total_eq = (tuple(coord for coord in all_unclicked), minecount)
            self.unique_equations.add(total_eq)
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

                        if combo not in self.impossible_combinations:                   # (('a',1),('c',0),...) is the format of each combo in 'self.impossible_mine_combos', obviously, as well
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
            groupN_to_eqs = dict()
            groupN_to_vars = dict()                                                 # group_n : {var1, var2, var3..}
            completely_grouped_eqs = set()
            # n_calls_of_add_eqs = 0

            def add_eqs_containing_current_var_to_current_group(group_n, variable):
                # nonlocal n_calls_of_add_eqs                                         # FOR DEBUG: I wanted to see how many times it ends up here. Turns out, 10-90 times depending on the test, which is not too bad since it comes right back in 90% of the cases.
                # n_calls_of_add_eqs += 1
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
                    # print("n_calls_of_add_eqs:", n_calls_of_add_eqs)
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
        

        # for each separated set of equations, do the following: for each group (group=alternative solutions for an equation like a+b=1), find at least one solution that's compatible with AT LEAST ONE alternative solution from EXACTLY ONE other group. Then for those compatible alt solutions, couple all of those to the NEXT group; this builds a chain of equations, where the first equation is linked to one equation, the next one to the previous and to the next, etc, and the last one is linked only to the previous one. AFTER 'chain_link_equations', continue to build all possible alternative answers from those
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
                        
                        # THIS IS PER altA! It's completely OK if the code goes here, it reduces time complexity later on; if the current altA is not compatible with any altB from the current group, then it's deleted from the 'compatibility_groups', because it's an impossible combination of variable values.
                        if not at_least_1_altA_compatible_with_groupB:          # if altA from groupA is viable, it will have added groups of viable altBs from every other group
                            del compatibility_groups[altA]                      # do not keep lonely equations in the dict 'compatibility_groups'
                            # NB! DO NOT 'break' here! That was a remnant from a previous version... sigh.
                        else:                                                   # if there are no shared variables between groupA (including altA) and groupB (including altB), then groups A and B ARE compatible (they don't restrict each other in any way) -> move on to next groupB
                            at_least_1_altA_compatible_with_groupB = True       # just to show what this means in reality! Writing clear the logic for future generations... or myself, maybe.
                            continue                                            # this means that entire groupA and groupB are compatible -> move on to the next altA (moving on to next GROUP A would be even better though)
                    
                    # this 'if' below SHOULD NEVER HAPPEN. Currently: OK, I fixed it, it does never happen.
                    if not next_round_groupA:                                   # if this happens, it means BIG TROUBLE occurring in this function. This means that none of the altAs were compatible with any of the altBs -> group A and B are not compatible -> NO SOLUTION POSSIBLE! This should NEVER happen since a universal solution must always be found.
                        # if a!= len(alternative_answers_per_eq)-2:
                        "TROUBLE"
                    # else:                                                     # this works well, but the tests break, because this returns before ALL possible solutions have been found! The idea behind this commented-out part is that it first looks for the obvious solutions, before using the heavier machinery of solution tree building. This saves computation in cases where there are many separate parts of 'self.front' and/or one or more of them is big, in 'botGame.py'.
                    #     if n_compatible_altBs == 1:
                    #         for value, variable in tuple(next_round_groupA)[0]: # at this point, 'next_round_groupA' consists of all the altB equations from groupB that were compatible with groupA! As there's only one equation now, all its variables have now been solved.
                    #             self.solved_variables.add((value, variable))
                    #         return [['stop', 'here']]
                comp_groups_and_starting_groups.append((compatibility_groups, starting_group))
            return comp_groups_and_starting_groups
                                     
        list_of_compGroups_startingGroup = chain_link_equations(alternative_answers_per_equation_per_set_of_eqs)
        for compatibility_groups, starting_group in list_of_compGroups_startingGroup:
            if compatibility_groups == 'stop':
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
               
        def join_comp_groups_into_solutions(compatibility_groups:dict) -> None:
            keyVars_to_keys = keyVars_to_keys_builder(compatibility_groups)
            n_groups = len(keyVars_to_keys.keys())
            possible_whole_solutions = []
            
            def traverse(this_alt, entered_alts_for_this_build, 
                possible_solution_build, already_handled_groups) -> None:

                already_handled_groups2 = already_handled_groups.copy()
                possible_solution_build2 = possible_solution_build.copy()
                entered_alts_for_this_build2 = entered_alts_for_this_build.copy()                
                
                if this_alt in compatibility_groups:                        # If this alt solution is not a key in 'compatibility_groups', then IT IS UNTRUE as it's incompatible with one or more other groups' every possible alt answer; in that case, do NOT handle this alt at all (do not (1) mark its variables' proposed values as possible solutions, and do not (2) mark the group that it presents as handled); if the current alt is NOT present as a key of 'compatibility_groups', IT IS INCOMPATIBLE WITH AT LEAST ONE OTHER GROUP. In English, if the current alt solution is not present as a key in 'compatibility_groups', it CANNOT EVER SATISFY ALL THE EQUATIONS that we know MUST be true using at least one combination of alt solutions.
                    group_of_this_alt = identify_group(this_alt)            # 'this_alt' is an alt answer for some group - 'identify_group(this_alt)' tells me WHICH group it belongs to. I want EXACTLY ONE alt answer for EACH group, as each group represents an original equation from the minesweeper map (a number cell, the equation of which is always true, so MUST be satisfied and MUST be compatible with all other groups!)
                    if group_of_this_alt not in already_handled_groups2:    # NB! So, I only want EXACTLY ONE alt solution per group. If an alt solution has already been handled, DO NOT HANDLE ANOTHER; that another alt solution will be handled in a whole another iteration of this 'traverse()'. (2) Comparison of sets in python; if the values in the set are the same, then the sets are 'equal' in the == comparison. Nice.

                        incompatible_alt_solution = check_for_disagreements(            # this cannot happen on the FIRST call of 'traverse()', but it CAN happen on subsequent later calls - the 'compatibility_groups' only ensure PAIR compatibility, not beyond than that!
                            this_alt, possible_solution_build2)
                        if incompatible_alt_solution:                                   # if this alt solution disagrees i.e. is incompatible with already-recorded alt solutions (one from each met group so far), then move on to the next 'proposed_matching_alt' (which may be of the same OR of different group!) NB! Do NOT mark the group of the current alt solution as handled if it's incompatible; this means that we still need to wait for a compatible alt to come by from this group, so I must NOT mark it as handled yet!
                            return

                        # this includes the current alt solution
                        for var, value in this_alt:                         # (('a',0), ('b',1), ...) a 'proposed_matching_alt' has this format. It's one alt solution to an equation that's derived from the minesweeper map and which has to have ONE alt solution, the other ones being untrue.
                            possible_solution_build2[var] = value           # there can be 1 or 2 per variable. If 2, it means that there is not enough information (yet) for solving this variable. If only 1 value, great, that means the value is now solved.
                        
                        already_handled_groups2.append(group_of_this_alt)   # Since the alt solution was picked, mark the respective group as handled. ATM this is unnecessary, since I'm traversing through the equations in the same chain order as they were linked earlier, but If I were to change that, then this check is needed (previously, I DID need this, but this is a good check also for debugging anyways!)

                        if n_groups == len(already_handled_groups2):
                            possible_whole_solutions.append(possible_solution_build2)
                            return                                          # if it's done, it's done. The possible next matches would be to a completely different group, AND it's not possible to gain more solutions from this one, as new groups and their alts are only ADDED in this 'traverse()', not removed, and we've already been to all groups -> return, don't continue!
                        
                        new_matches = compatibility_groups[this_alt]        # continue to matches of this alt solution ONLY if none of the values of this alt solution disagree with values that have already been recorded in 'possible_solution_build' as values of the variables
                        entered_alts_for_this_build2.add(this_alt)
                        
                        # only do this if the above has not been fulfilled; it's not possible to gain another answer by trying to add yet another alt solution in the case where all the equations (all groups) have already been satisfied, which is checked in the 'if' clause above. SO: for every set of new_matches, I want the info that was updated according to what happened in the specific alternative solution above; which alt solution ('proposed_matching_alt') was 'entered' (seen, processed), which 'group' (equation) in question was handled. Since all the alternatives in the above loop are indeed ALTERNATIVES, they are NOT all saved immediately! (that would be incorrect), instead that is done after the 'traverse()'s below!
                        if new_matches:
                            for new_match in new_matches:
                                if new_match not in entered_alts_for_this_build2:    # technically redundant, probably almost no effect regarding computing efficiency, BUT it's nice for clarity, and showing the logic still (even if double check)
                                    traverse(new_match, 
                                        entered_alts_for_this_build2, possible_solution_build2, already_handled_groups2)
                        
            # 'starting_group' is the group from where all arrows leave, and back to which no arrows return; an alt origin for an alt rooted tree, essentially!
            for alt_origin in starting_group:                                       # E.g.: ('d', 'e'), [(('d',1),('e',0)), (('d',0),('e',1))]. This quarantees that they build unidentical solution trees that together encompass all possible whole solutions.
                if alt_origin in compatibility_groups:                              # some might have been filtered out as they were no longer fitting ALL other groups; the whole key has been deleted from 'compatibility_groups' if it's not compatible with ANY alt solution from its paired group (paired equation)
                    seen_proposed_vectors = set()                                   # PER alt answer, of course - that's why it's initialized here and not at the top of this 'join_groups_into_solutions'
                    handled_groups = []
                    alt_solution_build = {}
                    traverse(alt_origin, seen_proposed_vectors, 
                        alt_solution_build, handled_groups)                         # 'traverse' builds alternative 'possible_whole_solutions' and saves all viable ones to 'possible_whole_solutions'
                
            def minecount(possible_whole_solutions):
                pass

            def handle_possible_whole_solutions():
                final_answers = dict()
                new_answer_count = 0
                for dictionary in possible_whole_solutions:
                    for var, val in dictionary.items():
                        if var not in final_answers:
                            final_answers[var] = val
                            new_answer_count += 1
                        elif final_answers[var] == 'either or':
                            pass                                                            # I need this for accurate 'new_answer_count'
                        elif final_answers[var] != val:
                            final_answers[var] = 'either or'                                # either this was 'either or' was here or not, the result is the same - 'either or'  
                            new_answer_count -= 1
                for var, val in final_answers.items():
                    if val != 'either or':
                        self.solved_variables.add((var, val))                               # reduces redundant work in 'update_related_info...' if ALL of these are added first, before the loop below calling that function for all of those newly solved variables.
                if new_answer_count == 0:
                    minecount(possible_whole_solutions)
            
            handle_possible_whole_solutions()
                
        for compatibility_groups, starting_group in list_of_compGroups_startingGroup:
            join_comp_groups_into_solutions(compatibility_groups)
        
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
                                self.update_related_info_for_solved_var(((var, value)))
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
                                    self.update_related_info_for_solved_var(((var, value)))
                return new_solutions
        # solution_finder_from_compatibility_groups(compatibility_groups)           # works, but I'm not using it.

    # NB! This is called, when adding new equations for the first time, AND after finding new variables IF the related equations are (1) new and (2) do not become single solved variables as well (i.e. if the related equations are not reduced from equations like a+b=1 to just solved single variables like b=1). Hence, sometimes the 'self.update_equation(equation)' is necessary.
    def handle_incoming_equations(self, equations:list) -> None:    # equations = [(x, y, ((x1, y1), (x2, y2), ...), summa), ...]; so each equation is a tuple of of x, y, unflagged unclicked neighbours (coordinates; unique variables, that is!), and the label of the cell (1,2,...8)
        self.unique_equations = set()
        self.variable_to_equations = dict()
        for x,y, variables, summa in equations:                     # (x,y, variables, sum_of_variables). The x and y are the origin of the equation - actually unnecessary at the moment, I'm not using it for anything atm.
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
        elif len(csp.solved_variables) == 0:
            print('- NO SOLVED VARIABLES!')
            return(name, 'failed', concat)
        if concat == expected_result:
            print('test passed!')
            return(name, 'passed', concat)
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
    # print_solved_variables(csp, name, expected_result) # expected cdefg 00110

    ########################## Test 6: letters. Minecount! Make a situation where there's one number cell '1' pointing to two adjacent cells, a and b, and there's also a third cell 'c' that's not seen by any number cell; it's boxed by flags. I just ran into a situation like this and the minecount didn't work; so this is truly a test for debugging! #
    
    eq1     = [-1, -1, ('a', 'b'), 1]                         
    
    name = 'test 6a, letters, MINECOUNT=1. c=0 expected.'
    csp = CSP_solver()
    csp.handle_incoming_equations([eq1])
    csp.absolut_brut(minecount=1, need_for_minecount=True, all_unclicked=['a','b','c'])                 # So, here 'a' and 'b' are seen by number cell that says '1'. So, a+b=1. But also, there's an isolated cell c in the corner, surrounded by three flags, hence not seen by any number cell. The wanted result here is that c=0, because the remaining minecount is 1, and a+b=1, so c=0.
    
    expected_result = '0'                                                                               # c=0
    test_info_dict[name] = [csp, expected_result]
    # print_solved_variables(csp, name, expected_result) # expected cdefg 00110

    print_multiple_results(test_info_dict)


'''
This class is exclusively for MinesweeperBot's botGame; hence, all equations are 1st order, and of the type 

    q*a + w*b + e*c +... = k

where all factors and variables ∈ N and k ∈[0,8] (NB: the original 'raw' equations fed into the 'CSP_solver' will never evaluate to less than 1; there would be nothing to solve in those kinds of equations, as the automatic answer would be 0 for all terms, as each term has to be 0 or 1)

In fact, all raw equations that come straight from the minesweeper map have factors (q,w,e above) = 1, because there is one of each neighbour for each cell.

All the operations I need for handling these equations are (1) subtraction between these linear equations and (2) the inspection of constraint that each cell ∈ {0,1}. This is done by checking if for example ...+2x+... = 1, where the only possible solution for x is x=0, since if x was 1, others would have to be negative, or if a+b+c+... = 0, which means that all terms are 0. This latter one (all 0) can happen only after initial processing, as (like mentioned above), no such equations come 'raw' from the map.
'''