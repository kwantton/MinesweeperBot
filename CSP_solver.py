# NB! 'sum' = the label of the cell in minesweeer map (the number seen on the cell)
# Searching: (1) variable_to_equations; get all equations that contain a specific variable, (2) self.json: get all the info about an equation; {equation : info_structures_here}. Together, these two enable efficient search of info about any equation based on the variable included in the equation
class CSP_solver:
    def __init__(self):
        #self.json = dict()                                 # self.json = eq{ { variable1 : count1, variable2 : count2 }, { count : set(variable1, variable2...) }, sum}: Why also count : set(variables)
        self.seen_xy = set()                                # Dunno if this will be needed. Per each (x,y) on the minesweeper map, the equations can change gradually, that's why this was created; to be able to update old info in case the equation is new but the (x,y) has already been seen before; in that case, I'd update the (x,y)-specific equation.
        self.unique_equations = set()                       # I want uniqe equations (=> not x,y) here: {(variables, sum)} it's possible to get the same equation from two sides, for example - and it's of course possible to mistakenly add the same thing multiple times        
        self.solved_variables = set()                       # ((x,y), value)
        self.variable_to_equations = dict()                 # { variable_a:set(equation5, equation12, equation4,...), variable_b:set(equation3, equation4...)}
        self.tried_equation_combinations = set()            # set(set(), set(),...). TO-DO! Implement this checking + adding in 'factor_one_solve'
        self.numberOfVariables_to_equations = {             # { numberOfVariables : set(equation1, equation2, ...) }; all equations with numberOfVariables = x. I want to look at those equations with low number of variables, and see for each of those variables if they can be found in equations with more variables.
            x:set() for x in range(1, 8+1)
        }        
        #self.xy_specific_equations = []                    # self.equations = y[ x[ eq{ { variable1 : count1, variable2 : count2 }, { count : set(variable1, variable2...) }, sum} ] ]: entry by [y][x], where y = row number, x = column number. Why also count : set(variables)
    
    # NB! the 'rounds=1' is arbitrary, and is convenient for debugging and visualization purposes. In 'botGame.py' I am calling one 'bot_move' per one press of key 'b' by the person running the program, and a part of each of these 'bot_move's is this 'factor_one_solve()' here. Therefore, for visualization and debugging purposes, I want to make it possible to advance one small step at a time; that's why I have the 'rounds=1' set by default. Also, performance-wise, there is no obvious way to tell if performing one or multiple of these rounds in a row is faster or not (on average; this depends on so many things, including the map itself!) without considering first if the simpler logic in 'bot_move' before this 'CSP_solver' has anything more to offer before this 'CSP_solver' is performed or not; so performance-wise, it's a bit of a (micro)mystery, at least yet, whether one should let this run for a longer time or not by default.
    def factor_one_solve(self, rounds=1):                                   # 'factor_one' here means that each variable has a factor of exactly one (or zero, mathematically speaking), no more, for this solver (e.g. a+b+c=2, never a+2b+c=2 for example, since each minesweeper map cell has exactly one of each neighbour). This should be enough; there should not be a need to sum equations in my case!
        equations_to_add = []                                               # these will have to wait for loop ending, otherwise 'Set changed size during iteration'
        for s in range(1, 8+1):                                             # s for short. Why to 8? Because a single '1' cell can have 8 neighbours; some of these neighbours can be shared with other cells in case of a compulsory guess having been made (the lonely '1' in the middle would be the guess then, obviously).
            if s in self.numberOfVariables_to_equations:
                short_equations = self.numberOfVariables_to_equations[s]    # gets all equations with 's' number of variables, 'shorty_vars' below
                for shorty in short_equations:
                    shorty_vars, shorty_sum = shorty                        # e.g. if the equation was a+b+c=1, then shorty_vars = (a,b,c) and shorty_sum = 1)
                    for l in range (s+1, 8+1):                              # l for the length of a potential longer-than-shorty equation
                        longer_equations = self.numberOfVariables_to_equations[l]   # 0 or more long_equations
                        for longy in longer_equations:
                            all_shorty_vars_found_in_this_longer_equation = True    # what this is for: if we have a+b+c = 1 (shorty) and a+b+c+d=1 (longy; it has more variables than 'shorty'), we get d=0 by subtracting shorty from longy. Or if shorty is 'a+b=1' and longy is 'a+b+c+d+e=2', then after subtraction we have c+d+e=1. That's why I'm checking if EVERY SINGLE variable in shorty is found in longy, before subtracting and registering the result as a potentially new equation (possibly solving a variable, OR helping later on with other equations). In the case of minesweeper, there should not be any case NEEDED where one has to do a subtraction where you end up with some terms negative; hence the check is justified.
                            longy_vars, longy_sum = longy
                            for variable in shorty_vars:
                                if variable not in longy_vars:
                                    all_shorty_vars_found_in_this_longer_equation = False
                                    break
                            if all_shorty_vars_found_in_this_longer_equation:
                                result_equation = (tuple(var for var in longy_vars if var not in shorty_vars), longy_sum - shorty_sum) # since factors for all variables are 1, for all variables that were found in both shorty and longy, they are subtracted to 0. As for the sum, it's the longy_sum - shorty_sum
                                if result_equation not in self.unique_equations:   # once again, technically this 'if' check is unnecessary, but it's better to write out the logic
                                    equations_to_add.append([-1,-1, (result_equation[0]), result_equation[1]]) # add_equations uses format [ [x, y, tuple(variables), int] ]. Since this a hybrid equation, let's say it has (x,y) of (-1,-1), as it doesn't have one definitive 'origin' coordinate (x,y)
                                    # self.add_equations([]) # OLD; you can't add them here, or 'Set changed size during iteration' since add_equations() will add to 'self.numberOfVariables_to_equations', which is being iterated over
                                    result_vars, new_sum = result_equation
                                    if len(result_vars) == 1:
                                        print("solved a new variable! Variable:", result_vars[0], "=", new_sum)
                                        self.solved_variables.add((result_vars[0], new_sum))
        
        self.add_equations(equations_to_add)
        if rounds > 1:
            self.factor_one_solve(rounds-1)

    def add_equations(self, equations:list):                            # equations = [(x,y,tuple(),sum), (x,y,tuple(),sum)]; so each equation is a tuple of a set consisting of x, y, unflagged unclicked neighbours (coordinates; unique variables, that is!), and the label of the cell (1,2,...8)
        for equation in equations:
            x, y, variables, total = equation
            if (variables, total) not in self.unique_equations:         # can't hash sets; variables has to be a tuple!
                variable_count = 0
                for variable in variables:
                    variable_count += 1
                    if variable not in self.variable_to_equations:
                        self.variable_to_equations[variable] = set()
                    self.variable_to_equations[variable].add((variables, total))        # the purpose of {variable : equations} is to be able to find all equations that have the variable
                    if (x,y) not in self.seen_xy:                                       # this 'if' clause is technically speaking redundant, as 'self.seen_xy' is a set() so .add() is ok even in the case of duplicates, but I still want to show the logic
                        self.seen_xy.add((x,y))        
                self.unique_equations.add((variables, sum))
                if variable_count not in self.numberOfVariables_to_equations:
                    self.numberOfVariables_to_equations[variable_count] = set()
                self.numberOfVariables_to_equations[variable_count].add((variables, total))
                #self.json[(variables, total)]
            # if (x,y) in self.seen_xy: # why 'if ((x,y) in self.seen_xy)'? Because per each (x,y) on the minesweeper map, the equations can change gradually; hence I am enabling an update to maintain the info about the specific (x,y) location. Will it be useful? Probably not, but just in case.

def format_equation_for_csp_solver(x:int, y:int, variables:tuple, surrounding_mine_count:int) -> list:
    # NB! 'variables' has to be a tuple OR something that can be converted to a tuple; so 
    variables = tuple(str(coordinate_tuple) for coordinate_tuple in variables)  # if there's a cell with (x,y) = (4,5) in self.front, then the variable name shall be '(4,5)'. Simple and effective. The constraint for each variable is [0,1], meaning that the solution for each variable has to be 0 or 1.
    input_addition = [x, y, variables, surrounding_mine_count]
    return input_addition

if __name__ == '__main__':

    ''' 
    Example: solving
    a + b = 1
    a + c + d = 1
    c + d + e = 2
    d + e = 1
    '''                                             # note that coordinates (x,y) do not matter regarding the solving itself; they are for bookkeeping
    eq1 = [0, 1, ('a', 'b'), 1]                     # (x,y) = (0,1), equation is 'a + b = 1' (the first one above in orange!)
    eq2 = [1, 1, ('a', 'c', 'd'), 1]
    eq3 = [2, 1, ('c', 'd', 'e'), 2]
    eq4 = [3, 1, ('d', 'e'), 1]
    csp = CSP_solver()
    csp.add_equations([eq1, eq2, eq3, eq4])
    csp.factor_one_solve()                          # PRINT: "solved a new variable! Variable: c = 1" which is correct
    
    ###### a minesweeper map, where X means 'unclicked' cell, * is a 'mine' cell (not seen by the player), and 1 is '1' cell, 2 is '2' cell. Every # is edge of the map, essentially means nothing
    #X*X*#
    #1121#
    ######
    
    # the above map is described by these inputs that are used as input for 'add_equations'
    c01 = [0, 1, ('(0,0)', '(0,1)'), 1]             # 'c01' means 'cell x=0 y=1'. There are 2 variables in C01, '(0,0)' and '(0,1)', and the sum of these two is 1. The variable names mean (x,y), and each variable is either 0 or 1, meaning the number of mines in that cell (x,y) of the minesweeper map.
    c11 = [1, 1, ('(0,0)', '(1,0)', '(2,0)'), 1]
    c21 = [2, 1, ('(1,0)', '(2,0)', '(3,0)'), 2]
    c31 = [3, 1, ('(2,0)', '(3,0)'), 1]
    csp = CSP_solver()
    csp.add_equations([c01, c11, c21, c31])
    csp.factor_one_solve()                          # PRINT: "solved a new variable! Variable: (1,0) = 1" which is correct! It means that (x,y) = (1,0) is a mine, which it indeed is.
        

'''
This class is exclusively for MinesweeperBot's botGame; hence, all equations are 1st order, and of the type 

    q*a + w*b + e*c +... = k

where all factors and variables ∈ N (NB: the original 'raw' equations will never evaluate to less than 1; there would be nothing to solve in those kinds of equations, as the automatic answer would be 0 for all terms, as each term has to be 0 or 1)

In fact, all raw equations that come straight from the minesweeper map have factors (q,w,e above) = 1, because there is one of each neighbour for each cell.

All the operations I need for handling these equations are (1) subtraction between these linear equations and (2) the inspection of constraint that each cell ∈ {0,1}. This is done by checking if for example ...+2x+... = 1, where the only possible solution for x is x=0, since if x was 1, others would have to be negative, or if a+b+c+... = 0, which means that all terms are 0. This latter one (all 0) can happen only after initial processing, as (like mentioned above), no such equations come 'raw' from the map.
'''

# IGNORE BELOW SKETCHING
'''

self.json = eq{ { variable1 : count1, variable2 : count2 }, { count : {variable1, variable2...} }, sum}:

        equation1 : {
            variables: {
                variable1 : count_of_variable1,
                variable2 : count_of_variable2,
                ...
            },
            counts: {
                1 : set(all variables with count 1 in the equation),
                2 : set(all variables with count 2 in the equation),
                ...
            }
            sum : int
        },

        equation2 : {...}
    ],

^^ above example: 2x2 map (a list of two lists (rows) with two items per list (row)), not very interesting

self.equations = y[ x[ eq{ { variable1 : count1, variable2 : count2 }, { count : {variable1, variable2...} }, sum} ] ]: entry by [y][x], where y = row number, x = column number
[
    [
        {
            variables: {
                variable1 : count_of_variable1,
                variable2 : count_of_variable2,
                ...
            },
            counts: {
                1 : set(all variables with count 1 in the equation),
                2 : set(all variables with count 2 in the equation),
                ...
            }
            sum : int
        },

        {...}
    ],

    [
        {...},
        {...}
    ]
]
^^ above example: 2x2 map (a list of two lists (rows) with two items per list (row)), not very interesting

self.which_equationss_have_variable_x = [[set()]], entry by [y][x] like above:
{
    equation1: {variable1, vari}
}

IDEAS:
- sort equations by length. Start with the shortest one, and see which of the other equations has all its terms -> subtract -> see if the new equation is unique. Efficient
'''