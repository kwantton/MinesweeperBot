'''to-do:
- 1-4 tests pass, there are 8 tests c: the new logic SHOULD be close to done, fingers crossed. Find out the problems!
'''
from itertools import combinations

# NB! 'sum' = the label of the cell in minesweeer map (the number seen on the cell)
# Searching: (1) 'variable_to_equations'; get all equations that contain a specific 'variable' as key, (2) self.json: get all the info about an equation; {equation : info_structures_here}. Together, these two enable efficient search of info about any equation based on the variable included in the equation
class CSP_solver:
    def __init__(self):

        self.unsolved_groups = set()                                    # add here all those equations (i.e. groups = alternative answers for an equation derived from the minesweeper map) that could not be solved
        self.unique_equations = set()                                   # { ((var1, var2, ..), sum_of_mines_in_vars), (...) }. Each var (variable) has format (x,y) of that cell's location; cell with a number label 1...8 = var. Here, I want uniqe EQUATIONS, not unique LOCATIONS, and therefore origin-(x,y) is not stored here. It's possible to get the same equation for example from two different sides, and via multiple different calculation routes, and it's of course possible to mistakenly try to add the same equation multiple times; that's another reason to use a set() here, the main reason being fast search from this hashed set.        
        self.solved_variables = set()                                   # ((x,y), value); the name of the variable is (x,y) where x and y are its location in the minesweeper map (if applicable), and the value of the variable is either 0 or 1, if everything is ok (each variable is one cell in the minesweeper map, and its value is the number of mines in the cell; 0 or 1, that is)
        self.impossible_combinations = set()
        
        self.variable_to_equations = dict()                             # { variable_a : set(equation5, equation12, equation4,...), variable_b : set(equation3, equation4...)}. The format of 'equation' is ((variable1, variable2,...), sum_of_the_variables)
        self.numberOfVariables_to_equations = {                         # { numberOfVariables : set(equation1, equation2, ...) }; each key of this dict is integer x, and x's values are all equations with x number of variables. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables; if all the variables in the shorter equation are found in the longer equation, then perform subtraction to get rid of those varibles in the longer equation (linear equation solving), then save the formed result equation to 'self.unique_equations' and 'self.numberOfVariables_to_equations'.
            x:set() for x in range(0, 8+1)                              # Why up to 8? Because a single '1' cell, resulting from a forced guess in the middle of unclicked cells, has 8 neighbours, hence 8 variables in the equation for that '1' cell; some of these neighbours can be shared with other cells in case of a compulsory guess having been made (the lonely '1' in the middle would be the guess then, obviously). NB! It's possible that when all variables in a given equation have just been solved, all are canceled out, and at that point the length of the equation (i.e. the number of variables) becomes 0; that's why I'm starting from 0.
        }                                                               # { numberOfVariables : set(equation1, equation2, ...) }; all equations with numberOfVariables = x. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables.
        self.var_to_equations_updated_equations_to_add = set()          # during iteration of these, these cannot be directly changed -> gather a list, modify after iteration is over
        self.var_to_equations_obsolete_equations_to_remove = set()      # same as above comment

    # 100% solution: (1) PER EACH EQUATION that MUST be satisfied (i.e. each number cell on the minesweeper map), try all combinations of ones (=mines). That's what THIS function does. (2) After this function below, from all of the alternative combinations of 1s and 0s that DO satisfy the CURRENT equation, find those alternatives that are incompatible with all other equations, pairing one group's all possible alts with compatible alts of ONE other group (i.e. "groups", i.e. incompatible with ALL the alternative solutions of at least one other group) (3) from the remaining alt equations per group (i.e. PER original equation), find columns where a variable is always 0 or 1 -> it HAS to be 0 or 1 ALWAYS. Then see these new solutions, inspect the remaining equations for untrue alternatives now that we've solved a new variable (or many new variables), and keep repeating the whole loop (1),(2),(3) as long as new solutions keep coming. Stop iteration when there are no longer new solutions produced by the whole loop.
    def absolut_brut(self) -> None:

        # for each equation (i.e. each number cell on the minesweeper map), given that each variable (= each unopened cell) is 0 or 1 (no mine or a mine), find all possible combinations of 1s and 0s that can satisfy that SINGLE equation GIVEN THAT it has sum = k (some integer number = the number of mines in those unopened surrounding cells in total!)
        def find_and_group_possible_answers_per_single_equation() -> list:                  
            alt_answers_per_equation = []
            for variables, summa in self.unique_equations:
                mine_location_combinations = combinations(variables, summa)         # all possible combinations of mines for this equation
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
            return alt_answers_per_equation
        alternative_answers_per_equation = find_and_group_possible_answers_per_single_equation()    # each group represents the answers for a single equation derived from a single number cell on the minesweeper map.

        # used in 'restrict_solution_space_as_equation_pairs_with_common_variables()' below; are there common variables between two equations (i.e. groups)?
        def common_vars(vars1, vars2) -> bool:
            common = False
            varsB = set(twople[0] for twople in vars2)                              # twople = (var, value), but obviously I can't name it 'tuple' since that's reserved in Python
            for twople in vars1:
                if twople[0] in varsB:
                    common = True
                    break
            return common

        # for each group (group=alternative solutions for an equation), find at least one solution that's compatible with AT LEAST one alternative solution from every other group (i.e. from every other equation that MUST be satisfied). Then continue from that!
        def restrict_solution_space_as_equation_pairs_with_common_variables(alternative_answers_per_eq:list) -> dict:
            compatibility_groups = dict()                                   # { possible solution : all related possible solutions (i.e. those which share variables and do not disagree for any variable value for those variables that are present in both the key and each of the values in this dictionary for that key!) }. There's no need for explicit bookkeeping regarding which of the value solutions belong to which original equation, because the variables included themselves are enough to identify the origin.
            # NB! I need to add the keys also for the last groupA even though it has no groupB to pair it with! This is because checks in later functions require the existence of viable alts in 'compatibility_groups' keys!
            for a in range(len(alternative_answers_per_eq)):                # e.g. ( (('a',0), ('b',1)), (('a',1),('b',0)) ) would constitute one 'group' (length 2) for the equation 'a+b=1' which is stored as ((a,b),1) in 'self.unique_variables'; that is, all the possible solutions for that equation constitute a 'group'
                if a == 0:
                    groupA = alternative_answers_per_eq[a]
                    starting_group = alternative_answers_per_eq[a]
                else:
                    groupA = sorted(tuple(next_round_groupA))               # from the previous round! Since this is from a set, it may become disordered -> for comparison if equal with groupB, sorting is needed!
                if a == len(alternative_answers_per_eq)-1:
                    for alt in groupA:
                        compatibility_groups[alt] = set()                   # all viable alts must be found in keys of 'compatibilty_groups'. On the last round, groupA is the compatible alt solutions of last round's groupB, and these are all ok. Therefore, all of them must be added to 'compatibility_groups'.
                    break
                b = a+1
                groupB = alternative_answers_per_eq[b]
                if groupA==groupB:
                    continue                                                # this never happens (GOOD! This is the expected result). It should NEVER happen as long as I don't change this whole function (again...), so it's good that it doesn't happen c:
                next_round_groupA = set()
                common_variables = common_vars(groupA[0], groupB[0])        # I want unilateral direction to ALL possible compatible alt solutions from ALL OTHER groups
                at_least_1_altA_compatible_with_groupB = False              # default. NB! groupB needs to be compatible for altA to be viable! That is: if altA is to be viable, it has to satisfy at least one altB from every groupB! (2) this ALSO checks if there are
                for altA in groupA:                                         # e.g. altA = (('a', 0), ('b', 1)); altA = alternative solution (i.e. ONE theoretically POSSIBLE solution) to the equation whose possible answers are members of groupA; altA = one alternative solution for a single equation, that might or might not be possible (i.e. might or might not be compatible with each groupB (i.e., with at least one possible answer of each other equation))
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
                            at_least_1_altA_compatible_with_groupB = True
                            compatibility_groups[altA].add(altB)            # I don't need to explicitly group this altB for this key; I know that those values which share the same variables belong to the same group (i.e. they originate from the same equation)!
                            next_round_groupA.add(altB)                     # on the next round, these ok altBs become groupA c:
                    
                    # THIS IS PER altA! It's completely OK if the code goes here; if the current altA is not compatible with any altB from the current group, then it's deleted from the 'compatibility_groups'
                    if not at_least_1_altA_compatible_with_groupB:          # if altA from groupA is viable, it will have added groups of viable altBs from every other group
                        del compatibility_groups[altA]                      # do not keep lonely equations in the dict 'compatibility_groups'
                        # NB! DO NOT 'break' here! That was a remnant from a previous version... sigh.
                    else:                                                   # if there are no shared variables between groupA (including altA) and groupB (including altB), then groups A and B ARE compatible (they don't restrict each other in any way) -> move on to next groupB
                        at_least_1_altA_compatible_with_groupB = True       # just to show what this means in reality! Writing clear the logic for future generations... or myself, maybe.
                        continue                                            # this means that entire groupA and groupB are compatible -> move on to the next altA (moving on to next GROUP A would be even better though)
                
                # this 'if' below SHOULD NEVER HAPPEN. Currently: OK, I fixed it, it does never happen.
                if not next_round_groupA:                                   # if this happens, it means BIG TROUBLE occurring in this function. This means that none of the altAs were compatible with any of the altBs -> group A and B are not compatible -> NO SOLUTION POSSIBLE! This should NEVER happen.
                    # if a!= len(alternative_answers_per_eq)-2:
                    "TROUBLE"
            return compatibility_groups, starting_group                     # remember! There's only ONE interpretation for those keys that have empty value set; they are NOT limited at all, that is, all alternatives (all 1-combinations, i.e. all mine combinations) are still possible for them!
        compatibility_groups, starting_group = restrict_solution_space_as_equation_pairs_with_common_variables(alternative_answers_per_equation)

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
                possible_solution_build, already_handled_groups):

                already_handled_groups2 = already_handled_groups.copy()
                possible_solution_build2 = possible_solution_build.copy()
                entered_alts_for_this_build2 = entered_alts_for_this_build.copy()                
                
                if this_alt in compatibility_groups:                        # If this alt solution is not a key in 'compatibility_groups', then IT IS UNTRUE as it's incompatible with one or more other groups' every possible alt answer; in that case, do NOT handle this alt at all (do not (1) mark its variables' proposed values as possible solutions, and do not (2) mark the group that it presents as handled); if the current alt is NOT present as a key of 'compatibility_groups', IT IS INCOMPATIBLE WITH AT LEAST ONE OTHER GROUP. In English, if the current alt solution is not present as a key in 'compatibility_groups', it CANNOT EVER SATISFY ALL THE EQUATIONS that we know MUST be true using at least one combination of alt solutions.
                    group_of_this_alt = identify_group(this_alt)            # 'this_alt' is an alt answer for some group - 'identify_group(this_alt)' tells me WHICH group it belongs to. I want EXACTLY ONE alt answer for EACH group, as each group represents an original equation from the minesweeper map (a number cell, the equation of which is always true, so MUST be satisfied and MUST be compatible with all other groups!)
                    if group_of_this_alt not in already_handled_groups2:    # NB! So, I only want EXACTLY ONE alt solution per group. If an alt solution has already been handled, DO NOT HANDLE ANOTHER; that another alt solution will be handled in a whole another iteration of this 'traverse()'. (2) Comparison of sets in python; if the values in the set are the same, then the sets are 'equal' in the == comparison. Nice.

                        incompatible_pma = check_for_disagreements(         # this cannot happen on the FIRST call of 'traverse()', but it CAN happen on later calls - the 'compatibility_groups' only ensure PAIR compatibility, not further than that!
                            this_alt, possible_solution_build2)
                        if incompatible_pma:                                # if this alt solution disagrees i.e. is incompatible with already-recorded alt solutions (one from each met group so far), then move on to the next 'proposed_matching_alt' (which may be of the same OR of different group!) NB! Do NOT mark the group of the current alt solution as handled if it's incompatible; this means that we still need to wait for a compatible alt to come by from this group, so I must NOT mark it as handled yet!
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
                        
           
            # 'starting_group' the group from where all arrows leave, and back to which no arrows return; an alt origin for an alt tree, essentially! (If I were to select just ONE origin (origin = a key in 'compatibility_groups' = ONE random alternative solution for one equation), it may be a non-ok alternative meaning that it may never become connected with ALL other equations via any of their alt solutions, thus never finding any whole solution that satisfies all equations. Therefore, at least I have to pick ALL alternatives for ONE single group, as alternative origins where 'traverse()' starts, to quarantee that some kind of a whole-solution is found. This is because the origins (key equations) are SINGLE ALTERNATIVES for one equation, and as we know, only ONE alternative may provide a possible answer for every group (depends on the case, actually - sometimes two alternatives are possible, if there is not enough information to be able to deduce in which one the mine is, for example! And/or if the groups are entirely disconnected!))
            for alt_origin in starting_group:                                       # ('d', 'e'), [(('d',1),('e',0)), (('d',0),('e',1))] for example. This quarantees that they are separate
                if alt_origin in compatibility_groups:                              # some might have been filtered out as they were no longer fitting ALL other groups; the whole key is deleted from the 'compatibility_groups' if it's not compatible with ANY alt solution from the paired group (values)
                    seen_proposed_vectors = set()                                   # PER alt answer, of course - that's why it's initialized here and not at the top of this 'join_groups_into_solutions'
                    handled_groups = []
                    alt_solution_build = {}
                    traverse(alt_origin, seen_proposed_vectors, 
                        alt_solution_build, handled_groups)                         # 'traverse' builds alternative 'possible_whole_solutions' and saves all viable ones to 'possible_whole_solutions'
                
            def handle_possible_whole_solutions():
                final_answers = dict()
                for dictionary in possible_whole_solutions:
                    for var, val in dictionary.items():
                        if var not in final_answers:
                            final_answers[var] = val
                        elif final_answers[var] != val:
                            final_answers[var] = 'either or'                                    # either this was 'either or' was here or not, the result is the same - 'either or'
                        
                for var, val in final_answers.items():
                    if val != 'either or':
                        self.solved_variables.add((var, val))                               # reduces redundant work in 'update_related_info...' if ALL of these are added first, before the loop below calling that function for all of those newly solved variables.
                for var, val in final_answers.items():
                    if val != 'either or':
                        self.update_related_info_for_solved_var((var, val))
            handle_possible_whole_solutions()
            pass
                

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
            
            # for the remaining compatibility_groups equations, all those that have propositions about wrong values for the newly solved variables are now known to not be true. Find those wrong equations and remove them (after iteration) from 'compatibility_groups'. Then, once again feed the now-updated 'compatibilty_groups' to the solver, 'solution_finder_from_compatibility_groups'
            def update_compatibility_groups(compatibility_groups:dict) -> dict:

                def all_variables_solved(keys) -> bool:
                    for key in keys:
                        for var, proposed_value in key:
                            if not ((var,0) in self.solved_variables or (var,1) in self.solved_variables):
                                return False
                    return True

                def check_proposed_value(var, proposed_value):
                    ok = True
                    opposite = (var, int(not(proposed_value)))
                    if opposite in self.solved_variables:
                        self.impossible_combinations.add(key)                               # the key is an equation like (('a',1), ('b',0)) just like each its equations (values)! The key can become outdated just like its values!
                        ok = False
                    return ok

                if all_variables_solved(compatibility_groups.keys()):                           # TO-DO! NB! This should be uncommented after you find the problem with the below/something else regarding the updating/the whole loop...
                    return 'all variables solved'
                else:
                    updated_compatibility_groups = dict()                                       # rebuild this according to the previous, 'new_solutions'
                    for key, values in compatibility_groups.items():                            # the old 'compatibility_groups' to be updated; check for (1) solved variables, (2) untrue alternative solutions (do not add those to the 'updated_compatibility_groups')
                        key_ok = True
                        for var, proposed_value in key:
                            key_ok = check_proposed_value(var, proposed_value)                  # the key is an equation like (('a',1), ('b',0)) just like each its equations (values)! The key can become outdated just like its values!
                            if not key_ok:
                                break
                        if key_ok:
                            if key not in updated_compatibility_groups:
                                updated_compatibility_groups[key] = set()                       # I don't want empty sets - don't add those keys at all
                            for proposed_vector in values:                                      # (a) if the proposed value is not the solved value, then this 'proposed_vector' (the whole line, with multiple variables and their proposed values) is untrue, and should be discarded
                                all_values_ok = True
                                for var, value in proposed_vector:
                                    all_values_ok = check_proposed_value(var, value)
                                    if not all_values_ok:
                                        break
                                if all_values_ok:
                                    updated_compatibility_groups[key].add(proposed_vector)      # only add the non-obsolete vectors (var,value -pair tuples) to the 'updated_compatibility_groups'
                return updated_compatibility_groups                  
            new_solutions = key_altSolution_inspector()
            if new_solutions:
                updated_compatibility_groups = update_compatibility_groups(compatibility_groups)        
                if updated_compatibility_groups == 'all variables solved':
                    return
                elif updated_compatibility_groups:
                    solution_finder_from_compatibility_groups(updated_compatibility_groups)             # RECURSION. TO-DO: last test is infinite; how is it even possible? The thing preventing infinite recursion is the check 'return new_solutions' from 'simple_inspection()'; it only returns those variables that were not already in 'self.solved_variables' previously. Hence, if the loop returns nothing new, it's stopped at that point.
        # solution_finder_from_compatibility_groups(compatibility_groups)



























    # NB! This is called, when adding new equations for the first time, AND after finding new variables IF the related equations are (1) new and (2) do not become single solved variables as well (i.e. if the related equations are not reduced from equations like a+b=1 to just solved single variables like b=1). Hence, sometimes the 'self.update_equation(equation)' is necessary.
    def add_equations_if_new(self, equations:list) -> None:                             # equations = [(x, y, ((x1, y1), (x2, y2), ...), summa), ...]; so each equation is a tuple of of x, y, unflagged unclicked neighbours (coordinates; unique variables, that is!), and the label of the cell (1,2,...8)
        for equation in equations:                                                      # (x,y,(variables),sum_of_variables)
            x, y, variables, summa = self.update_equation_and_related_info(equation)    # both updates, IF NECESSARY, 'self.unique_equations' (removes the old one, adds the shorter one), AND returns the new one here right away. NB: this small sidetrack is very short in cases where an equation is truly added for the first time (such as in 'botGame.py' from where this 'CSP_solver' class is used)
            variables = tuple(sorted(variables))
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
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
    csp.absolut_brut()       # TO-DO; fails sometimes, even if 2 ... 10 rounds! (why sometimes; because sets can be handled in undeterministic order relative to each other)     # PRINT: see answer above in orange
    
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
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
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
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
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
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
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
    csp.add_equations_if_new([eq1, eq2, eq3, eq4])
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
    csp.add_equations_if_new([c01, c11, c20, c21])
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
    csp.add_equations_if_new([eqi, eqiii, eqv, eqvi, eqa, eqb])
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
    csp.add_equations_if_new([eq1, eq2, eq3, eq4, eq5])
    csp.absolut_brut()                                  # NB! This needs 2 rounds!

    
    expected_result = '00110000'
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