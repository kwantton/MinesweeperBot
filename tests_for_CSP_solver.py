from CSP_solver import CSP_solver

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

name = 'Test 8a: Expert_minecount-solvable_1. c0, d1, e1, f0, g0, i0, j0, t0 expected' # NB! This was true BEFORE I added an early return from minecount in 'CSP_solver', which can save HUGE amounts of work (it avoids the heaviest minecount calc in situations where SOME vars are solved more easily from 'simple minecount' as I like to call it (i.e. either only min n mines is possible, OR only max n mines is possible)); i.e., in the simplest minecount cases, if variables are solved, return early; this is also the in the situation of this test -> now ony 3 variables come out, sadly, in one go. Sad.
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