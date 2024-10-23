from CSP_solver_old import CSP_solver

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
csp.factor_one_binary_solve()       # TO-DO; fails sometimes, even if 2 ... 10 rounds! (why sometimes; because sets can be handled in undeterministic order relative to each other)     # PRINT: see answer above in orange
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
csp.factor_one_binary_solve()

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
csp.factor_one_binary_solve()                          
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
csp.factor_one_binary_solve()                          
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
csp.factor_one_binary_solve()

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
csp.factor_one_binary_solve()

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
csp.factor_one_binary_solve(3)                                  # NB! after 3 rounds minimum, e=0 is solved! A smaller number of rounds is not enough. This is ok and expected given the functions written in the class, as not everything is recursively updated until the end of the world (as this would complicate things even more!); also, nb! The purpose is not to be able to solve everything in one go, as that would also mean that pressing 'b' once in 'botGame.py' would proceed a huge number of steps at a time, AND this has nothing to do, as such, with efficiency either; so I want to divide this into small(ish) steps whenever possible, facilitating visualization and debugging that way, as there's no real reason not to do this. In fact, efficiency-wise, it's better to run as little as CSP_solver as possible, instead relying on the much simpler 'simple_solver' in 'botGame.py' as possible

print_solved_variables(csp, 'test 4a, letters. 0 expected', '0')

########################## Test 5a: letters. Based on 'Esim_expert_1.png', which wasn't solved by pressing 'b' (i.e., this test is for actual debugging) #

eq1     = [-1, -1, ('a', 'b'), 1]                         
eq2     = [-1, -1, ('a', 'b', 'c', 'd', 'e'), 2]
eq3     = [-1, -1, ('d', 'e', 'f'), 2]
eq4     = [-1, -1, ('e', 'f', 'g'), 2]
eq5     = [-1, -1, ('f', 'g', 'h', 'i', 'j'), 1]

csp = CSP_solver()
csp.add_equations_if_new([eq1, eq2, eq3, eq4, eq5])
csp.factor_one_binary_solve(2)                                  # NB! This needs 2 rounds!
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