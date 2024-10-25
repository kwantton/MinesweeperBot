import pygame
from time import time, sleep
from random import sample
from CSP_solver_old import CSP_solver as CSP_solver_old
from CSP_solver import CSP_solver, format_equation_for_csp_solver
from constraint_problem_solver_for_testing import check_if_solutions_were_missed_in_lost_game
from cell_id_names import flag, unclicked, mine, labellize, read_number_from_label


# cell = a clickable square of the minesweeper map, 'ruutu'. 'Label' = the id of a cell, like '0' or 'flag'.
class Minesweeper:
    '''
    The actual Minesweeper game and its interface are in this class.

    Note! Also `simple_solver()` is here. It handles the very simplest cases - it was convenient to keep
    here as it required much less work than moving all the relevant info back and forth
    to `CSP_solver` class just for the simplest of cases.

    Testing of lost games: 'constraing_problem_solver_for_testing.py' which finds if logic was missed in a lost game.
    '''
    
    def __init__(self, map_measurements:tuple, csp_on=True, minecount_demo_number = None, 
                 logic_testing_on = False, unnecessary_guesses = False):
        pygame.init()
        pygame.display.set_caption('MINESWEEPER')
        width, height, mines = map_measurements
        self.cells_to_open = width*height - mines
        
        # Note! Put here ONLY those that are not reset at every 'new_game()'
        self.mines = mines
        self.width = width
        self.auto_on = False                            # if set to true, then the bot will play as long as it hits a mine or wins; no need to smash p or b manually
        self.csp_on = csp_on
        self.height = height                            # map height measured in rows
        self.perpetual = False
        self.infobar_height = 100                       # pixels for the infobar above the minesweeper map
        self.ms_bot_time_TOTAL = 0
        self.visual_autobot = False                     # when this is on, the 30 fps screen draw is ON. This limits the speed of the bot, but looks cool :D press v to activate, WHEN you have pressed a
        self.logic_testing_on = logic_testing_on           # when this is on, for every lost game, a check will commence in 'constraint_problem_solver_for_testing.py'
        self.minecount_demo_number = minecount_demo_number

        if self.minecount_demo_number:
            self.height = self.width = 9
        
        self.clock = pygame.time.Clock()

        if (self.width, self.height, self.mines) in [expert, intermediate]:
            self.cell_size = 50-int(0.8*height)                             # how many px in height and width should each cell be?
        else:
            self.cell_size = max(18, min(50, 800 // max(self.width, self.height)))    # dynamic cell size calculation based on map dimensions
        self.draw_width = max(self.cell_size*width, 1000)
        self.initialize_debug_features(unnecessary_guesses)
        self.game_result_counter = [0,0]                # [wins, losses]
        
        self.font = pygame.font.Font(None, max(36-int(0.5*height), 25))     # min size is 25 now for the font
        
        if mines >= width*height-9:
            raise ValueError(f'too many mines, max is {width*height-9} for this size')
        
        self.images = {}                                # {name : loaded image}
        self.load_images()
        self.screen = pygame.display.set_mode((self.draw_width, self.cell_size*height + self.infobar_height + self.instructions_height), pygame.RESIZABLE) # each .png is 100 px, which is large. Extra height for info bar above the minesweeper map, and instructions bar below the minesweeper map
        
        self.new_game()
        self.loop()

    def initialize_debug_features(self, unnecessary_guesses:bool) -> None:
        '''
        Initializes visual interface features, which are togglable by pressing buttons listed below.
        '''
        print('\ninitialize_debug_features()')
        self.guesses = 0                                                            # keep a counter of how many guesses there were in total in all the games played so far
        if self.logic_testing_on:
            self.missed_logic_count = 0
        self.show_mines = False
        self.highlight_front = False                                                # 'front' cells = number-labeled cells that neighbour unsolved cells, i.e. cells in x € {1,2,...8} that do not have x flags marked around them. When this is 'True', it draws a yellow rectangle around each such cell.
        self.solved_by_minecount = 0
        self.highlight_guesses = False
        self.highlight_csp_solved = False
        self.highlight_minecount_solved = False
        self.instructions = '''
        a : automatic bot play (pressing "a" mid-game will stop the game; you can see where the bot ended up)
        v : toggle visual, 30 fps version of "a" (you also need to press "a" after this to use auto bot play)
        i : toggle infinite mode of "a"; if the bot loses or wins, it will start another game. PRESS ALSO "a" after this to start!
        x or n : single bot move (you can mash them as fast as you want)
        f : front highlighting
        c : highlight csp-solved cells
        h : highlight minecount-solved cells
        spacebar : new game
        g : highlight guessed cells (latest guess is golden, others are blue)
        m : show mine locations
        q: quit'''.split('\n        ')                                              # This way of writing lists is used a lot on the 'Data analysis with Python' course, it's very handy for writing longer lists quickly. This splits at each '\n        ' to form a list.
        self.unnecessary_guesses = unnecessary_guesses
        self.instructions_height = 20 + len(self.instructions)*30                   # pixels for the instructions bar below the minesweeper map

    def load_images(self):
        print('\nload_images')
        image_names = ['images/' + name + '.png' for name in '0 1 2 3 4 5 6 7 8 flag mine unclicked has_to_have_a_mine safe'.split()]
        for image_name in image_names:
            self.images[image_name] = pygame.transform.scale(pygame.image.load(image_name), (self.cell_size,self.cell_size))

    def reset_timer_vars(self):
        self.start_time = 0
        self.current_time = 0
        self.elapsed_bot_ms = 0                                                     # used for BOT timer in screen drawing
        self.finishing_time = 0
        self.autobot_end_time = 0
        self.elapsed_nonbot_s = 0                                                   # will be used for `self.finishing_time`
        self.ms_time_summed = False                                                 # for summing the ms elapsed time in case using autobot, EXACTLY ONCE, and not more times, to self.ms_time_summed, each game
        self.autobot_start_time = 0       
    
    def new_game(self):                     # i.e. initialize all appropriate variables at the start of every game
        print('\n-----------------------------')
        print("NEW_GAME")
        self.start_x = 0
        self.start_y = 0
        self.front = set()                  # number cells (1...8) that still provide information needed for solving / guessing as-of-yet unprobed cells
        self.opened = set()                 # all thus-far opened cells {(x0,y0), (x1,y1),...}, updated when new cells are opened

        self.started = False                # the mines will be placed AFTER the first click, as in real minesweeper. Otherwise you could lose on the first click. For that, we need to keep track on if the first click has already commenced or not.
        self.victory = False
        
        self.mouse_pos = (0,0)
        
        self.hit_a_mine = False
        self.game_ended = False
        self.latest_guess = None
        self.solver = CSP_solver()          # the main, all-capable solver, which is used if easier methods don't work
        self.guessed_cells = set()
        self.obsolete_front = set()         # all those members of 'self.front' that no longer have any unclicked unflagged neighbours
        
        self.solved_variables = set()                                               # needed for bookkeeping of what variables not to rehandle as solved_variables also come from CSP_solver
        self.new_front_members = set()                                              # this set is needed in 'add_new_front_cells_to_self_front()' for bookkeeping so that after iteration through 'self.front', the members of this set can be added to self.front. 'self.front' cannot be modified DURING iteration over itself, so that's why.
        
        self.solver_old = CSP_solver_old()                                          # the old, non-complete CSP_solver, which is very fast but can't solve everything. Used before CSP_solver (the new one)
        self.finished_using_autobot = False                                         # needed for accurate choice between ms timer and standard timer in case autobot was used (=in case automatic bot playing was used)        
        self.n_unclicked = self.width * self.height
        self.solved_new_using_simple_solver = False                                 # if True, continue with simple_solver() (continue with that as long as possible, only go to CSP_solver if simple_solver() is no longer enough)
        
        self.minecount = self.mines
        self.map = [[unclicked for x in range(self.width)] for y in range(self.infobar_height, self.height + self.infobar_height)]   # map = all the mines. Since the infobar is on top, the '0' y for mines = infobar_height. This map records the names of the images of each cell on the map.

        self.reset_timer_vars()

    def reset_vars_at_start_of_bot_execute(self):
        self.solver.guess = None                                                    # why? Because if 'self.solver.guess', 
        self.solved_new_using_simple_solver = False                                 # if True, continue with simple_solver() (continue with that as long as possible, only go to CSP_solver if simple_solver() is no longer enough)
        

    def autobot_loop(self) -> None:
        '''
        this loop is performed ~'instead of' the normal 'self.loop()' if you press 'i' in the interface. This
        enables starting a new game, playing it until finish, and restarting as long as you want. Handy!
        '''
        print("AUTOBOT LOOP")    
        while True:
            if self.auto_on:                                                        # this loop itself can set it off -> break the loop, go back to 'self.loop()' instead
                self.check_victory()                                                # sets 'self.game_ended = True', etc
                for event in pygame.event.get():
                    self.inspect_event(event)                                       # if you press 'a' again, this loop will break (among all the other things that are inspected in this 'inspect_event()' as well)
                if not self.game_ended:
                    if not self.started:
                        self.handle_first_left_click(self.start_x, self.start_y)    # this also starts the timer
                    else:
                        self.bot_act()  
                else:
                    self.auto_on = False
                    if not self.finished_using_autobot:
                        self.autobot_end_time = time()                              # without checking, this would increase a bit after every press of a even if the game has for exampled finished already
                        self.elapsed_bot_ms = (self.autobot_end_time - self.autobot_start_time) * 1000
                        if not self.ms_time_summed:
                            self.ms_time_summed = True
                            self.ms_bot_time_TOTAL += self.elapsed_bot_ms
                        self.finished_using_autobot = True
                        print("TIME (ms):", round((self.autobot_end_time-self.autobot_start_time)*1000,1))
                        if not self.visual_autobot:
                            self.draw_display()
                    if self.perpetual:
                        self.auto_on = True
                        self.new_game()
                    break

                if self.visual_autobot:
                    self.draw_display()
            else:
                break                                                               # go back to 'self.loop()' instead, when not 'self.autobot'
    def inspect_event(self, event) -> None:
        '''
        inspect pygame events; this is only called if there ARE pygame events
        '''
        if event.type == pygame.KEYDOWN:                                            # I have to check this first to be able to escape from the autobot loop when I so want
            if event.key == pygame.K_q:                                             # let's have a chance to escape asap, so that this doesn't go to the bottom of the list of things to do
                exit()
            elif event.key == pygame.K_a:
                self.auto_on = not self.auto_on
            elif event.key == pygame.K_i:
                self.perpetual = not self.perpetual
            elif event.key == pygame.K_v:
                self.visual_autobot = not self.visual_autobot
            elif event.key == pygame.K_SPACE:                                         # event.key, not event.type, sigh. I was looking for this with cats and dogs
                self.new_game()
            elif event.key in [pygame.K_x, pygame.K_n]:
                if not (self.hit_a_mine or self.victory):                           # I want to enable smashing 'b' and 'p' repeatedly without risking of error; after hitting a mine, smashing 'p' or 'b' can result in error (and can cause (more) lag)
                    if not self.started:
                        self.handle_first_left_click(self.start_x, self.start_y)
                    self.bot_act()                                                      # the bot makes a move when you press b
            elif event.key == pygame.K_m:
                self.show_mines = not self.show_mines
            elif event.key == pygame.K_f:
                self.highlight_front = not self.highlight_front                     # toggle debug; highlighting the frontline (rintama) of not-yet-solved portion of the map, on/off toggle
            elif event.key == pygame.K_g:
                self.highlight_guesses = not self.highlight_guesses
            elif event.key == pygame.K_c:
                self.highlight_csp_solved = not self.highlight_csp_solved
            elif event.key == pygame.K_h:
                self.highlight_minecount_solved = not self.highlight_minecount_solved
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f'MOUSEBUTTONDOWN;')
            mouse_x, mouse_y = pygame.mouse.get_pos()

            cell_x = mouse_x // self.cell_size                                      # cell_y = clicked minesweeper map cell y-coordinate, starting from 0, max at self.height-1 (where self.height = number of rows)
            cell_y = (mouse_y - self.infobar_height) // self.cell_size              # Like explained in the above comment. Implementation here: adjust for the infobar by 'raising' the click by infobar height, then get the row number by division by self.scale. Asked from ChatGPT when trying to find the problem with the y-location
            if (cell_y < 0) or (cell_y >= self.height) or (cell_x < 0) or (cell_x >= self.width):
                pass                                                                # if you click the top bar, it starts a new game
            elif event.button == 1:                                                 # left click == 1!
                print(f'- cell_x, cell_y: {cell_x, cell_y}')                        # if each cell width is e.g. 100 px, then if you click e.g. on x-coord 540, it's the 6th column (40 would be 1st)
                if not self.started:
                    self.handle_first_left_click(cell_x, cell_y)
                else:
                    self.probe(cell_x, cell_y, primary=True)
            elif event.button == 3:                                                 # right click == 3!
                self.toggle_flag(cell_x, cell_y)
        elif event.type == pygame.QUIT:
            exit()
    
    def handle_first_left_click(self, x:int, y:int) -> None:
        '''
        no matter if a human plays or if a bot plays, this ALWAYS is performed 1st. You can see that timers start here,
        start coordinates (where the 1st click occurred) happen here, etc., and 'self.generate_map()' is performed
        AFTER the first click (the reason is, that minesweeper always ensures that the 1st click is not a mine)
        '''
        print('\nhandle_first_left_click()')
        self.start_x = x                                                            # If you click the map in the beginning, the start coordinates are where you first click. If you don't click, but instead press b right away to let the bot make the first move, then by default 'self.start_x' = 'self.start_y' = 0 (top left corner of the map).
        self.start_y = y
        self.started = True
        self.generate_map(x, y)
        self.start_time = pygame.time.get_ticks()
        self.autobot_start_time = time()
        self.probe(x, y, primary=True)

    def generate_map(self, mouse_x:int, mouse_y:int) -> None:
        '''
        Based on the coordinates of the first clicked cell (mouse_x, mouse_y), place the mines ELSEwhere.
        Minesweeper always ensures that the 1st click is not a mine.
        Also, the first clicked cell is ensured to be 0 in classical minesweeper - that's how I'm doing it also.
        '''
        print('\ngenerate_map()')
        if self.minecount_demo_number:
            self.generate_simple_minecount_demo(self.minecount_demo_number)
        else:
            danger_x = set(x for x in range(self.width) if x-1 <= mouse_x <= x+1)
            danger_y = set(y for y in range(self.height) if y-1 <= mouse_y <= y+1)
            available_coordinates = [(x,y) for y in range(self.height) for x in range(self.width) if not x in danger_x or not y in danger_y]
            self.mine_locations = set(sample(available_coordinates, self.mines))   # NB! This line of code 'generates' the map by deciding mine locations! This samples a 'self.mines' number of mines (e.g. 99 in an expert game) from 'available_cordinates' which excludes the opening cell that was clicked.
        # print(f'- clicked coordinates {mouse_x, mouse_y} and placed the mines as follows:\n', self.mine_locations)
    
    def generate_simple_minecount_demo(self, demo_number:int) -> None:
        '''
        for quickly showing what minecount is (it's an equation
        whose sum is the number of remaining mines in the map at the moment, BUT
        it must be used wisely, ONLY when needed; otherwise you could have an equation with
        450 variables (expert map has 480 cells!) and {450 \choose 90} combinations. Yeah, would be bad.)
        '''
        self.height = self.width = 9
        self.minecount = self.mines = demo_number + 1
        self.cells_to_open = self.width*self.height - self.minecount        # exact same formula as normally (normally would be width*height-mines, but here minecount is correct for this)
        if demo_number == 1:
            self.mine_locations = set([(1,7), (2,6)])                        # 1 mine after normal solving, minecountable solution
        elif demo_number == 2:
            self.mine_locations = set([(0,7), (1,8), (2,6)])               # 2 mines after normal solving, NO solution
        elif demo_number == 3:
            self.mine_locations = set([(0,7), (1,8), (0,8), (2,6)])        # 3 mines after normal solving, minecountable solution
        

    def probe(self, x:int, y:int, primary=False) -> None:           # if primary = False, then don't go to 'handle_probing_of_already_opened_cell', otherwise it can loop and cause another chord! The chording is meant ONLY for actual chording
        '''
        Probe occurs whenever you left click on a cell, no matter what the cell is 
        (unclicked, already open, flag, mine). Clicking of already open cells can lead to chording 
        if the criteria are met (this is normal minesweeper functionality)
        '''
        # print(f'\nprobe({x,y}, from primary={primary});')
        if self.map[y][x] == flag:                                  # NB! This has to come first, as this is most probably in 'self.mine_locations'; If you left click on a red flag (i.e. 'probe' a flagged cell), it does nothing (like in real minesweeper)
            return
        elif (x, y) in self.mine_locations:                         # NB! This has to come before the 'unclicked' check; otherwise the next would be true, as all mine-containing cells are 'unclicked' (the tile's name is 'unclicked'!) before clicking c:
            self.map[y][x] = mine
            self.n_unclicked -= 1
            self.handle_game_lost(x,y)
            return
        elif self.map[y][x] == unclicked:
            self.handle_opening_a_new_cell(x, y)                    # this also adds the (x,y) to 'self.opened', which is needed to recognize victory, and for the 'if' clause below.
        elif (x, y) in self.opened and primary:
            # only if 'probe()' was not called from 'chord()'!
            self.handle_probing_of_already_opened_cell(x,y)         # it's possible that this is a chording, but you can't know that unless you check the number of marked flags around the cell first

    def handle_game_ended(self):
        '''
        after the game has ended in a victory or a loss
        '''
        self.game_ended = True
        self.finishing_time = pygame.time.get_ticks()
        self.elapsed_nonbot_s = (self.finishing_time - self.start_time) / 1000

    def check_victory(self) -> None:
        '''
        A minesweeper game is won if and only if all non-mine cells have been probed (=opened). 
        This has "DIRECTLY" nothing to do with whether you're using flags or not 
        (although, of course, if you flag non-mine cells, you can't win the game unless you first remove
        those erroneously placed flags, and then open those cells!)
        '''
        if len(self.opened) == self.cells_to_open:
            if not self.victory:
                self.victory = True
                self.game_result_counter[0] += 1
                self.handle_game_ended()

    def handle_game_lost(self, x:int, y:int) -> None:
        '''
        called AFTER a mine has been hit
        '''
        if not self.hit_a_mine:                                                 # my game counter increases after a lost game, so I'm making sure this happens only once
            print('game_over(): HIT A MINE AT COORDINATES:', (x, y))
            self.hit_a_mine = True
            self.game_result_counter[1] += 1
            self.handle_game_ended()
        if self.logic_testing_on:
            self.check_logic_completeness(x, y)
    
    def check_logic_completeness(self, x, y):
        self.save_lost_game_equations_for_inspection()
        self.draw_display()
        # sleep(5)
        
        self.missed_logic_count += check_if_solutions_were_missed_in_lost_game(self.last_lost_game, 
            remaining_mines_in_map=self.minecount, all_vars_in_remaining_map=self.get_all_unclicked_cells(), x=x, y=y)
        if self.missed_logic_count:
            self.auto_on = False    # STOP so I could see what happened. Never happened so far (luckily c:) but this would be very handy in case logic was missed! Also, this IS very handy when running with 'unnecessary_guesses = True' for testing of the tester 'constraint_problem....py'. Then you can directly look at the game and see what went wrong / where the unnecessary guess was.
            self.perpetual = False
    
    def save_lost_game_equations_for_inspection(self) -> None:
        '''
        saves the current lost game's equations to 'eq_list'. Then those eqs can be fed to a
        solver to see, if solutions were missed!
        '''
        eq_list = []
        for eq in self.solver.unique_equations:
            eq_list.append(eq)        
        self.last_lost_game = eq_list
        print('GAME LOST')
        self.draw_display()                                                     # I want to see what happened at this point, not a million years later after the checking is (perhaps) complete


    def handle_probing_of_already_opened_cell(self, x:int, y:int) -> None:
        '''
        This kind of a probing (when humans play) is either a "chording", or a "wasted click" (=it doesn't do anything)
        '''
        # print('\nhandle_probing_of_already_opened_cell()')
        neighbours = self.get_neighbours_of(x, y)                               # finds all the actual cells neighbouring (x,y)
        n_surrounding_flags = self.count_flags(neighbours)
        label = self.map[y][x]
        if label == labellize(n_surrounding_flags):
            self.handle_chord(x, y)                                             # if the number of surrounding flags = number of the cell, then open all non-flagged neighbours. Normal minesweeper functionality.
        else:
            pass

    def handle_opening_a_new_cell(self, x:int, y:int) -> None:
        '''
        ALL NEW CELL OPENINGS GO HERE, doesn't matter how the cell was opened (player/bot/single click/chord)
        '''
        # print('\nhandle_opening_of_a_new_cell()')
        self.n_unclicked -= 1
        self.opened.add((x, y))                                                 # why: in case a zero is clicked open, I'm using handle_click recursively to open up all the surrounding cells that are not mines. For that, this list is needed, so that an endless recursion doesn't occur.
        neighbours = self.get_neighbours_of(x, y)

        surrounding_mines = 0
        for neighbour in neighbours:
            if neighbour in self.mine_locations:                                # NB! 'self.mine_locations' is the set of ACTUAL mine locations, so this is correct
                surrounding_mines += 1
        self.map[y][x] = labellize(surrounding_mines)
        if surrounding_mines == 0:
            for neighbour in neighbours:
                self.probe(neighbour[0], neighbour[1], primary=True)            # this is normal minesweeper; whenever a 0 is clicked, all the neighbouring 0s, AND each of the neighours of each 0 are opened as well (i.e., the 0-front stops at numbers 1,2,...8). However, I can't know how many of the neighbours have already been opened, flagged, etc, so 'self.probe()' is the function to use, as it does the sorting automatically
        else:
            self.new_front_members.add((x,y))                                   # In the bot version, I can't directly do this because 'self.front' is being iterated through; you can't add new members to the iterated set during iteration, so I'm gathering the new members here to be added AFTER each entire run-through of 'self.front'

    def get_neighbours_of(self, x:int, y:int) -> list:                          # returns a list of tuples [(x1,y1), (x2,y2),...]
        neighbours = [(w,h) for h in range(y-1, y+1+1) for w in range(x-1, x+1+1) if 0 <= w < self.width and 0 <= h < self.height and (w,h) != (x,y)]    # this returns ALL the neighbours; no matter if 0,1,2,3,4,5,6,7,8,flag,mine,whatever
        return neighbours

    def count_flags(self, neighbours:list) -> int:
        count = 0
        for n in neighbours:
            if self.map[n[1]][n[0]] == flag:
                count += 1
        return count

    def count_cells_of_type(self, counted_cell_type:str, coordinates:list) -> int:
        count = 0
        for c in coordinates:
            if self.map[c[1]][c[0]] == counted_cell_type:
                count += 1
        return count

    def get_cells_of_type(self, wanted_cell_type:str, coordinates:list, negative=False) -> list:
        # print(f'\nget_cells_of_type({wanted_cell_type})')
        l = []
        for c in coordinates:
            if negative:
                if self.map[c[1]][c[0]] != wanted_cell_type:
                    l.append(c)    
            else:
                if self.map[c[1]][c[0]] == wanted_cell_type:
                    l.append(c)
        return l

    def handle_chord(self, x:int, y:int):
        # print('\nchord')
        neighbours = self.get_neighbours_of(x,y)
        # print(f'- ({x,y}) neighbours:', neighbours)
        for neighbour in neighbours:
            if self.map[neighbour[1]][neighbour[0]] == unclicked:                       # without this, it would chord also flagged cells
                self.probe(neighbour[0], neighbour[1])

    def toggle_flag(self, x:int, y:int) -> None:
        '''
        'self.n_unclicked' records how many cells with identity `unclicked` there are; hence, when you
        place a flag, it will decrease. When you remove a flag, it will increase.
        '''
        if self.map[y][x] == flag:
            self.map[y][x] = unclicked
            self.n_unclicked += 1
            self.minecount += 1                                                             # 'minecount' is the number visible on top left of the infobar. It simply is `self.mines - the Number Of Flags On The Map Currently`. This is a standard minesweeper feature, and needed to deduce the locations of the remaining mines in some near-map-end situations when there normally would be several ways to place the remaining mines, but using remaining minecount, some of these alternatives can be proved impossible.
        elif self.map[y][x] == unclicked:
            self.map[y][x] = flag
            self.n_unclicked -= 1
            self.minecount -= 1

    def get_all_unclicked_cells(self) -> set:                                               # needed below in two functions
        not_clicked = set()
        for x in range (self.width):
            for y in range (self.height):
                if self.map[y][x] == unclicked:
                    not_clicked.add((x,y))
        return not_clicked
    
    def bot_act(self) -> None:                                                              # before this, if started with 'b', there's been in order (1) 'self.handle_first_left_click()' (2) 'self.generate_map()' (3) 'self.probe()'
        # print('\nbot_act():')                                                             # the following prints will be '- something', '- something_else'. I like this way of console printing because it makes it faster to search for the useful stuff at a given moment in the console, and makes it clear which print originates from which function.
        
        def brain() -> None:

            def remove_obsolete_front() -> None:
                for coordinate in self.obsolete_front:                                      # why not remove them already during the 'for x,y' loop above? Because you can't remove an item from an iterable while it's being iterated over, otherwise, in this case, you'll get 'RuntimeError: Set changed size during iteration'
                    if coordinate in self.front:
                        self.front.remove(coordinate)
                self.obsolete_front.clear()

            def add_new_front_cells_to_self_front() -> None:
                for member in self.new_front_members:
                    self.front.add(member)
                self.new_front_members.clear()                                              # now that they are added, reset this list for the next round of bot_act()

            def filter_front_cells() -> None:
                ''' 
                This is an efficient and straightforward way of removing 
                obsolete front cells from 'self.front' in one go.

                For each cell in 'self.front', it checks if it has unclicked neighbours. 
                If not, it removes all those cells from 'self.front'.
                '''
                add_new_front_cells_to_self_front()                                         # I switched the order of 'add_new..' and 'remove_obsolete...' around; the only way to make absolutely sure that no obsolete front survives the filtering is to (1) FIRST add the new self.front members and (2) from THESE ALSO, filter out the unneeded ones (obsolete ones).
                for x,y in self.front:
                    neighbours = self.get_neighbours_of(x, y)
                    n_unclicked_unflagged_neighbours = self.count_cells_of_type(unclicked, neighbours)
                    if n_unclicked_unflagged_neighbours == 0:
                        if (x,y) in self.front:
                            self.obsolete_front.add((x,y))
                remove_obsolete_front()
            

            def check_minecount_zero() -> None:
                '''
                Only when playing using the bot.
                The bot ONLY flags cells where it has deduced that a mine is located with 100% certainty. 
                Hence, the minecount number on top right of the minesweeper game (standard feature)
                tells the player (and the bot!), how many mines remain. If that's 0, then open
                every remaining cell -> game won. Very simple.
                '''
                if self.minecount == 0:
                    for x,y in self.get_all_unclicked_cells():
                        self.probe(x,y,True)

            def get_unclicked_unseen_cells() -> set:
                '''
                'unclicked unseen cell' = a cell that's not seen by 'self.front'. Play a game and press 'f' to
                highlight all the 'self.front' cells, and you will quickly see what I mean (literally).

                These are extremly important for minecount logic AND for probability calculation, where
                these 'uu cells' each have the same probability of being a mine, and every cell next to 
                'self.front' can have different probabilities (largely speaking of course).
                '''
                adjacent_to_front = set()
                unclicked_unseen_cells = self.get_all_unclicked_cells()                      # this is filtered below! So at this point, this name is misleading.
                for x,y in self.front:
                    unclicked_front_cell_neighbours = self.get_cells_of_type(unclicked, self.get_neighbours_of(x,y))
                    for neighbour in unclicked_front_cell_neighbours:
                        adjacent_to_front.add(neighbour)
                for cell in adjacent_to_front:
                    unclicked_unseen_cells.remove(cell)
                return unclicked_unseen_cells
            
            def simple_solver() -> None:    
                '''
                The loop "for x,y in self.front" below finds SIMPLE (non-CSP) solutions:
                these are the very simplest solutions that any beginner minesweeper player uses: 
                (1) where the number of neighbouring unflagged unclicked cells + flagged cells equals to the label 
                -> flag all unflagged neighbours,
                (2) if label = number of surrounding flags, 
                then perform a chord (= a chording = opening all non-flag surrounding cells)
                Then, I remove unnecessary cells from the 'self.front' 
                to cut unnecessary computing work for the `CSP solver`.
                '''
                self.solved_new_using_simple_solver = False                                                                  # do not go to csp_solver if csp_solver has solved new variables during this round; instead return (so that you can repeat, by pressing 'b' or 'p' again c:)
                for x,y in self.front:
                    neighbours = self.get_neighbours_of(x,y)                                                    # self.bot_x and self.bot_y had been initially set in self.handle_first_left_click as the x (column number) and y (row number) of the first click
                    unflagged_unclicked_neighbours = self.get_cells_of_type(unclicked, neighbours)              # this is indeed 'unclicked unflagged neighbours', since label 'unclicked' means exactly that; the picture for 'unclicked' is an unprobed cell. A big confusing perhaps, I know.

                    if len(unflagged_unclicked_neighbours) > 0:                                             # if not, there's NOTHING to solve here! (unless someone had placed too many flags around, for example)
                        label = self.map[y][x]    
                        n_surrounding_flags = self.count_cells_of_type(flag, neighbours)

                        if label == labellize(len(unflagged_unclicked_neighbours) + n_surrounding_flags):   # If the number of surrounding ('unclicked' + 'flag') cells equals to the label of this (x,y) front cell in question (for example, 1 flagged + 2 unclicked = 3 = the label of the cell),
                            flag_these(unflagged_unclicked_neighbours)                                      # then flag the remaining unflagged cells around the front cell in question (flag the remaining 2 unclicked cells in this example case).
                            self.solved_new_using_simple_solver = True
                        elif label == labellize(n_surrounding_flags):         # NB! 'if', not 'elif'. Think what happens if n_surrounding_flags = x and un. If the number of flagged neighbours equals to the label of the current front cell,
                            self.solved_new_using_simple_solver = True
                            self.handle_chord(x,y)                                          # then open all of them (i.e. 'chord' at this current front cell (x,y)).
                
                check_minecount_zero()                                                          # if minecount is zero, then probe all 'unclicked' cells, since they cannot be mines -> map completed! Of course, this requires, that all the flags were placed correctly by the bot (they always are). This situation needs separate handling because the last 'unclicked' cells can be inside completely flagged boxes, isolating them from 'self.front'. It took me 5 weeks to even arrive in that kind of a situation! It's extremely rare, as it needs at least 3 already-flagged cells in a cordner, or 5 in a center edge, or 8 or more in the middle! Awesomesauce.
                filter_front_cells()

            def feed_csp_solver():
                '''
                After removing thus far redundant cells from the 'self.front' (done in 'update_front'), 
                I'm feeding equations into my `CSP_solver` (= self.solver). There, more complex solving happens.
                '''
                csp_solver_input = []                                                                   # a list of lists; [ [x, y, ('var_a', 'var_b', 'var_c', ...), label_of_cell], [...], ...]; each inner list represents a set of (1) (x,y), (2) variables to try to solve (cells, which can have value 0 or 1), (3) the total number of mines (sum) of those variables
                for x,y in self.front:
                    surrounding_mine_count = read_number_from_label(self.map[y][x])                     # all 'self.front' cells have number labels, number = 1,...8 (not 0). It cannot be 0, since we just removed those cells from 'self.front' in the 'for...' loop above
                    neighbours = self.get_neighbours_of(x,y)
                    unflagged_unclicked_neighbours = self.get_cells_of_type(unclicked, neighbours)
                    n_surrounding_flags = self.count_flags(neighbours)
                    csp_solver_input_addition = format_equation_for_csp_solver(x, y, unflagged_unclicked_neighbours, surrounding_mine_count - n_surrounding_flags)    # NB! 'surrounding_mine_count - n_surrounding_flags' was what I was missing for two days; it caused solving of WRONG equations in the CSP_solver(). I.e.; what if there are flags around, not just unflagged neighbours? That's why there's the '- n_unflagged_neighbours' subtraction. They have to be removed from the total minecount.
                    csp_solver_input.append(csp_solver_input_addition)
                self.solver.handle_incoming_equations(csp_solver_input)
                self.solver_old.reset_all()                                                             # reset all before new round
                self.solver_old.add_equations_if_new(csp_solver_input)

            def csp_solve() -> bool:
                '''
                This uses the `CSP_solver_old` and `CSP_solver` classes. 
                If `simple_solver()` wasn't enough, CSP_solver_old is used.
                If CSP_solver_old wasn't enough, CSP_solver is used.
                The solving functionality is in `CSP_solver.absolut_brut()`, and the instance
                of `CSP_solver` used is here the variable 'self.solver'. So
                `self.solver.absolut_brut()` is called with the necessary parameters
                '''
                print('\ncsp_solve():')

                solved_new_using_old_csp = False
                self.solver_old.factor_one_binary_solve()
                solved_vars = self.solver_old.solved_variables                  # set of tuples: each is a tuple ((x,y), value)
                
                for (x,y), value in solved_vars:
                    if ((x,y), value) not in self.solved_variables:             # avoid repeating already-done work
                        if value == 1:
                            flag_these([(x,y)])
                        elif value == 0:
                            self.probe(x, y)
                        self.solved_variables.add(((x,y), value))               # for avoiding repeating work in the future
                        solved_new_using_old_csp = True
                if solved_new_using_old_csp:                                    # VERY often this finds solutions -> next round; do not use heavier machinery than needed!
                    print('✔ FOUND SOLUTIONS FROM OLD CSP SOLVER')
                    filter_front_cells()
                    return solved_new_using_old_csp

                all_unclicked_cells = self.get_all_unclicked_cells()
                unclicked_unseen_cells = get_unclicked_unseen_cells()
                n_unclicked_unseen_cells = len(unclicked_unseen_cells)
                
                self.solver.absolut_brut(n_mines_remaining = self.minecount,        # the right top of normal minesweeper shows this number
                    all_unclicked = all_unclicked_cells,                            # all unclicked cells (excludes flagged ones)
                    unclicked_unseen_cells = unclicked_unseen_cells,                # unclicked cells that are not neighbours of 'self.front'
                    number_of_unclicked_unseen_cells = n_unclicked_unseen_cells)    # the number of the cells above
                solved_vars = self.solver.solved_variables                          # set of tuples: each is a tuple ((x,y), value)
                solved_new = False
                for (x,y), value in solved_vars:
                    if ((x,y), value) not in self.solved_variables:         # avoid repeating already-done work
                        if value == 1:
                            flag_these([(x,y)])
                        elif value == 0:
                            self.probe(x, y)
                        self.solved_variables.add(((x,y), value))           # for avoiding repeating work in the future
                        solved_new = True
                if self.solver.minecount_successful:
                    self.solved_by_minecount += 1
                filter_front_cells()                                        # 'self.front' has to be kept up-to-date. It's simple: if a self.front member is no longer surrounded by any unclicked unflagged cells, it is no longer in self.front.
                return solved_new
            
            def guess_preferably_uu() -> tuple:
                '''
                this is only in the rarest of special cases, when `CSP_solver` timeout timer is exceeded
                in the worst cases (currently it's set to 10 seconds per solving round). This random_guess()
                chooses a random cell only, if no unseen unclicked cells remain at all.
                '''
                for x, y in self.front:
                    for n in self.get_neighbours_of(x,y):
                        if self.map[y][x] == unclicked:
                            return x,y
                for x in range (self.width):
                    for y in range (self.height):
                        if self.map[y][x] == unclicked:
                            return x,y

            def pick_optimal_unclicked_unseen_cell_for_guessing() -> tuple:
                '''
                returns:    the cell (can be string or tuple!) which should be guessed next 
                This is 'naively optimal', only considering this round's least dangerous cell, not what happens after the guess.
                '''
                
                top_left = 0,0
                top_right = self.width-1, 0
                bottom_left = 0, self.height-1
                uu_cells = get_unclicked_unseen_cells()
                bottom_right = self.width-1, self.height-1
                highest_chance_of_zero = top_left, top_right, bottom_left, bottom_right # indeed, highest chance of zero WITHOUT considering unclicked cells seen by self.front. Are these magically more safe to click, however? No, but the chance of 0 is highest in the corners, since they only have 3 neighbours! Why do I want a 0? Because it has the highest chance of uncovering usable logic.
                for candidate in highest_chance_of_zero:
                    if candidate in uu_cells:
                        return candidate                            # get the first available corner. Why? Corners' chance of being 0 is the highest
                else:
                    for x in range(self.width):                     # go through the sides; chance of 0 there is 2nd highest (corners have highest, as only 3 neighbours, but at this point, they are all used up. Sad)
                        if (x,0) in uu_cells:
                            return x,0
                    for y in range(self.height):
                        if (self.width-1, y) in uu_cells:
                            return self.width-1, y
                    for x in range(self.width):
                        if (x, self.height-1) in uu_cells:
                            return x, self.height-1
                    for y in range(self.height):
                        if (0, y) in uu_cells:
                            return 0, y

                    for cell in self.front:                         # if all the sides are used up, try behind the front.
                        neighbours = self.get_neighbours_of(x=cell[0], y=cell[1])
                        for x, y in neighbours:
                            if self.map[y][x] == unclicked:
                                n_2 = self.get_neighbours_of(x, y)
                                for n in n_2:
                                    if n in uu_cells:
                                        print('returning neighbour of neighbour of self.front cell')    # this often reveals more about the situation at 'self.front'. A generally 'good' strategy. Always optimal? No.
                                        return n
                for cell in uu_cells:                               # if there are no suitable neighbours' neighbours, then just pick the first unclicked unseen cell that you come across
                    return cell
                return None                                         # if there are no uu_cells (I'm only needing this in case I'm using a timer timeout in CSP_solver in the worst cases! Never else is this used (I know because I had played tens of thousands of games without this before implementing this c:))

            def guess(cell_to_open) -> None:                        # I'm not specifying the 'cell_to_open' as string of tuple, as both can be used.
                '''
                parameters: cell_to_open; can be string or tuple
                returns:    Nothing. Performs the guessing via `probe(cell_to_open)`
                '''
                self.guesses += 1
                if cell_to_open in ['pick unclicked', 'timeout']:
                    cell_to_open = pick_optimal_unclicked_unseen_cell_for_guessing()
                if cell_to_open == None:
                    cell_to_open = self.solver.front_guess
                if cell_to_open == None:                            # ONLY if I set a timeout timer in `CSP_solver`, otherwise this was never needed (not in 18 000 expert games, at least c:)
                    cell_to_open = guess_preferably_uu()            # ONLY in case of timer timeout in `CSP_solver`
                self.guessed_cells.add(cell_to_open)
                self.latest_guess = cell_to_open                    # for highlighting the LATEST guess also, very convenient for seeing what just happened
                self.probe(x=cell_to_open[0], y=cell_to_open[1])

            def bot_execute():
                '''
                ACTUAL BOT LOGIC EVENT CHAIN IS HERE: this performes the above functions in order.
                Like you see, if 'self.solved_new_using_simple_solver = True', it RETURNS instead of
                going to csp_solve(). The purpose is to reduce the number of equations going to 
                `CSP_solver` as much as possible. It also looks much better as the bot plays in
                smaller increments this way.
                '''
                self.reset_vars_at_start_of_bot_execute()               # resets 'self.solved_new_using_simple_solver', self.solver.guess
                simple_solver()

                if self.solved_new_using_simple_solver:                 # IF 'simple_solver()' IS ENOUGH, DO NOT PROCEED FURTHER! Only use the heavier machinery (csp_solve()) if necessary.
                    return

                feed_csp_solver()                                       # this also resets all old csp solver vars

                if self.csp_on:                                         # (1) it uses self.solver_old, and if that doesn't help (incomplete logic), then self.solver, which is capable of solving everything and calculating probabilities, but it's slower
                    new_vars_solved = csp_solve()

                if (self.solver.guess and not new_vars_solved) or self.unnecessary_guesses:       # (1) NORMAL USAGE: if CSP_solver has not managed to solve any new variables with 100% certainty ('normal' logic OR minecounting logic), THEN guess. This info is directly obtained from 'self.solver', as you can see (`if self.solver.guess`) (2) TESTING TESTING USAGE: if `self.unnecessary_guesses`, then guesses are done -> the lost game missed logic tester in 'constraint_problem_solver_for_testing.py' will notice that missing logic was found, and the 'missing_logic' counter will increase and turn red, proving that it works. Awesome!
                    guess(self.solver.guess)                            # 'self.solver.guess' is the variable that had the highest probability of NOT being a mine (as of 12.10.2024 at least)

            bot_execute()

        def flag_these(cells) -> None:                              # NB! this ensures that a flag is placed in all, only when appropriate
            for x,y in cells:
                if self.map[y][x] == unclicked:                     # NB! this ensures that a flag is placed in all, only when appropriate
                    self.toggle_flag(x,y)
        brain()

    def draw_display(self) -> None:
        '''
        draw everything that's needed on the screen. If certain things are highlighted, highlight those
        (highlight_front, highlight_csp_solved, etc)
        '''
        RED = (255,0,0)
        GREEN = (0,255,0)
        WHITE = (255,255,255)

        self.screen.fill((0,0,0))

        def draw_minecount() -> None:
            minecount_surface = self.font.render(f'Mines left: {self.minecount}', True, WHITE)
            self.screen.blit(minecount_surface, (10,10))

        def draw_timer() -> None:
            if not self.started:
                shown_time = '0'
                if not self.visual_autobot:
                    shown_time += ' ms'
            elif not self.game_ended:
                self.current_time = pygame.time.get_ticks()
                shown_time = f'{((self.current_time - self.start_time) // 1000)}'
            else:                                                                                       # GAME END: hit a mine or won; GAME ENDED:
                if self.finished_using_autobot and not self.visual_autobot:
                    ms_time = self.elapsed_bot_ms                                                       # autobot timer; the goal is to be as precise as possible
                    shown_time = f'{ms_time:.1f} ms'
                    if ms_time > 1000:                                                                  # it usually is less than 1000 ms, so that's why it's the default
                        shown_time = f'{(ms_time / 1000):.3f} s'
                else:
                    shown_time = f'{self.elapsed_nonbot_s:.3f} s'                                       # b after clearing the map, show exact time
            timer_surface = self.font.render(f'Time: {shown_time}', True, WHITE)                # 'self.elapsed_time' is 0 by default
            self.screen.blit(timer_surface, (10, 55))

        def write_ms_average():
            n_games = sum(self.game_result_counter)
            if n_games:
                ms_time_average = self.ms_bot_time_TOTAL / n_games
                if ms_time_average > 1000: # then show seconds, not milliseconds
                    s_time_average = ms_time_average / 1000
                    ms_average_surface = self.font.render(f'average: {s_time_average:.3f} s/game', True, WHITE)                # 'self.elapsed_time' is 0 by default
                else:
                    ms_average_surface = self.font.render(f'average: {ms_time_average:.0f} ms/game', True, WHITE)                # 'self.elapsed_time' is 0 by default
                self.screen.blit(ms_average_surface, (10, 75))

        def draw_victory() -> None:
            if not self.hit_a_mine:
                text = 'MAP CLEARED!'
                y = 10
                x = self.draw_width-230
            else:
                text = '.. and completed'                                                                   # if you hit a mine AFTER you've completed the game, acknowledge this c:
                y = 50
                x = self.draw_width-230
            victory_surface = self.font.render(text, True, GREEN)
            self.screen.blit(victory_surface, (x, y))

        def draw_hit_a_mine() -> None:
            hit_a_mine_surface = self.font.render(f'HIT A MINE!', True, RED)
            self.screen.blit(hit_a_mine_surface, (self.draw_width-230, 10))
            draw_minecount()
            draw_timer()

        def transparent_highlight_surface(r,g,b,a) -> pygame.Surface:
            highlight_surface = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)           # I want to have alpha for the highlights so they don't cover everything. For this, I asked ChatGPT
            highlight_surface.fill((r,g,b,a))                                                               # R,G,B,alpha. Asked ChatGPT to get the alpha
            return highlight_surface

        def highlight_front_cells_yellow() -> None:                                                         # highlight yellow every cell that's in 'self.front'. This is for visualization and debugging in the bot_logic development                  
            surface = transparent_highlight_surface(255,255,0,128)
            for x,y in self.front:
                self.screen.blit(surface, (x*self.cell_size, y*self.cell_size + self.infobar_height))

        def highlight_csp_solved() -> None:
            mine_surface = transparent_highlight_surface(255,0,0,128)
            safe_surface = transparent_highlight_surface(0,255,0,128)
            for (x,y), mine in self.solver.solved_variables:
                if mine:
                    self.screen.blit(mine_surface, (x*self.cell_size, y*self.cell_size + self.infobar_height))
                else:
                    self.screen.blit(safe_surface, (x*self.cell_size, y*self.cell_size + self.infobar_height))

        def highlight_minecount_solved() -> None:
            mine_surface = transparent_highlight_surface(255,0,126,128)
            safe_surface = transparent_highlight_surface(0,255,126,128)
            for (x,y), mine in self.solver.minecount_solved_vars:
                if mine:
                    self.screen.blit(mine_surface, (x*self.cell_size, y*self.cell_size + self.infobar_height))
                else:
                    self.screen.blit(safe_surface, (x*self.cell_size, y*self.cell_size + self.infobar_height))

        def highlight_mines_red() -> None:
            surface = transparent_highlight_surface(255,0,0,128)
            try:                                                                                    # if the first click has not been done, there are no self.mine_locations. I didn't want to create an empty one, as the initialization section of this class is so big already, I don't want to bloat it more.
                for x,y in self.mine_locations:
                    self.screen.blit(surface, (x*self.cell_size, y*self.cell_size + self.infobar_height))
            except:
                pass

        def highlight_guesses_blue() -> None:
            guess_surface = transparent_highlight_surface(0,0,255,128)
            latest_guess_surface = transparent_highlight_surface(255,255,0,128)
            for x,y in self.guessed_cells:
                if (x,y) != self.latest_guess:
                    self.screen.blit(guess_surface, (x*self.cell_size, y*self.cell_size + self.infobar_height))
            if self.latest_guess:
                # if self.latest_guess not in self.mine_locations:                                    # it looks ugly if the mine is red + blue + green, almost opaque and weird
                    self.screen.blit(latest_guess_surface, 
                    (self.latest_guess[0]*self.cell_size, self.latest_guess[1]*self.cell_size + self.infobar_height))

        def write_minecount_success():
            minecount_success_surface = self.font.render(f'minecount success', True, GREEN)
            self.screen.blit(minecount_success_surface, (self.draw_width-230, 35))

        def write_p_success_front():
            p_success_surface = self.font.render(f'Front ≤ {self.solver.p_success_front} % safe', True, WHITE)
            self.screen.blit(p_success_surface, (self.draw_width-230, 55))

        def write_p_success_unseen():
            p_success_surface = self.font.render(f'other ~ {self.solver.p_success_unseen} % safe', True, WHITE)
            self.screen.blit(p_success_surface, (self.draw_width-230, 75))

        def write_unclicked_cell_count():
            p_success_surface = self.font.render(f'unclicked cells: {self.n_unclicked}', True, WHITE)
            self.screen.blit(p_success_surface, (10, 30))

        def write_number_of_games_solved_by_minecount():
            count_surface = self.font.render(f'minecount solutions: {self.solved_by_minecount}', True, WHITE)
            self.screen.blit(count_surface, (self.draw_width-550, 10))
        
        def write_number_of_guesses_so_far():
            count_surface = self.font.render(f'total guesses: {self.guesses}', True, WHITE)
            self.screen.blit(count_surface, (self.draw_width-550, 30))
        
        def write_choice():
            choice = 'other'
            if self.solver.choice == 'FRONT':
                choice = 'safest front cell'
            choice_surface = self.font.render(f'guess: {choice}', True, WHITE)
            self.screen.blit(choice_surface, (self.draw_width-550, 50))

        def write_wins_and_losses():
            wins, losses = self.game_result_counter
            total = wins + losses

            wins_surface = self.font.render(f'won: {wins}', True, WHITE)
            total_surface = self.font.render(f'games: {total}', True, WHITE)
            losses_surface = self.font.render(f'lost:  {losses}', True, WHITE)

            self.screen.blit(wins_surface, ((300, 30)))
            self.screen.blit(total_surface, ((300, 10)))
            self.screen.blit(losses_surface, ((300, 50)))

            if wins or losses:
                percent_won = round(100 * wins / total, 1)
                percent_won_surface = self.font.render(f'% won: {percent_won}', True, WHITE)
                self.screen.blit(percent_won_surface, ((300, 70)))
        
        def write_missed_logic_count():
            logic_inadequate_count = self.missed_logic_count
            color = GREEN
            if logic_inadequate_count != 0:
                color = RED
            logic_error_count = self.font.render(f'missing logic: {logic_inadequate_count}', True, color)
            self.screen.blit(logic_error_count, ((self.draw_width-550, 50)))


        def draw_map() -> None:
            for x in range (self.width):
                for y in range(self.height):
                    cell_status = self.map[y][x]                                                    # self.map is a list of lists; indices start from 0
                    self.screen.blit(source=self.images[cell_status], dest=(x*self.cell_size, y*self.cell_size+self.infobar_height))

        def draw_instructions_bar() -> None:
            start_y = self.height * self.cell_size + self.infobar_height - 10
            for i, instruction in enumerate(self.instructions):                                     # it isn't possible to use a multiline text, so each instruction has to be drawn separately. For this solution, I asked ChatGPT.
                instruction_surface = self.font.render(instruction, True, WHITE)
                self.screen.blit(instruction_surface, (10, start_y + i * 30))                       # draw all the instructions beneath each other

        if self.victory:
            draw_victory()
        if self.hit_a_mine:                                                                         # I'm enabling both, in case someone wants to try to finish it still
            draw_hit_a_mine()
        
        draw_minecount()
        draw_timer()
        write_ms_average()
        draw_map()
        draw_instructions_bar()
        write_unclicked_cell_count()
        write_wins_and_losses()
        write_number_of_games_solved_by_minecount()
        write_number_of_guesses_so_far()
        if self.highlight_front:
            highlight_front_cells_yellow()
        if self.show_mines:
            highlight_mines_red()
        if self.highlight_csp_solved:
            highlight_csp_solved()
        if self.highlight_minecount_solved:
            highlight_minecount_solved()
        if self.highlight_guesses:
            highlight_guesses_blue()
        if self.solver.minecount_successful:                                # if minecount() in CSP_solver solved variables succesfully, then write 'minecount' in the upper bar. Else, guessing, and write that info instead.
            write_minecount_success()
        if self.logic_testing_on:
            write_missed_logic_count()
        else:
            if self.solver.p_success_front != None:                         # it can be zero!
                write_p_success_front()
            if self.solver.p_success_unseen != None:                        # why? this too can be zero c:
                write_p_success_unseen()
            if self.solver.choice:
                write_choice()

        pygame.display.flip()                                               # display.flip() will update the contents of the entire display. display.update() enables updating of just a part IF you specify which part
        self.clock.tick(30)

    def loop(self) -> None:
        '''
        the loop of the pygame game. It goes to 'autobot_loop()' instead, if 'self.auto_on == True'
        '''
        print('LOOP')
        while True:                                                         # I'm enabling continuing after hitting a mine as well
            self.check_victory()                                            # here, 'self.finishing_time' is recorded, IF the game is won
            if self.auto_on:                                             # if autobot is on, then play as fast as possible. Otherwise, only inspect events if an event occurs
                self.autobot_loop()
                self.draw_display()                                             # (2) then draw the screen after handling them
            else:
                for event in pygame.event.get():
                    self.inspect_event(event)
                self.draw_display()                                             # (2) then draw the screen after handling them

if __name__ == '__main__':

    '''
    Testing:

    if 'logic_testing_on = True' as a parameter below, then every lost game will be checked for missing logic 
    in 'constraint_problem_solver_for_testing.py'.
        For convenience, when using that, press 'i' and then 'a' in the game; this will toggle on the
    infinite playing mode (which can be toggled off by pressing 'i' again.
    Finishing current game can be toggled off by pressing 'a' again).
        Testing CAN stall forever in an EXPERT game, as the validity testing is slow in cases of a
        lot of variables (it lists all possible solutions)!

    -------------------------------------------------------
    HOW TO PROVE THAT THE LOST GAME CHECKING WORKS? Answer:
    -------------------------------------------------------

    (1) ctrl-f (find) the following, here in botGame.py:

    `if self.solver.guess or self.unnecessary_guesses:                 # (1) NORMAL USAGE: if CSP_solver has not managed to solve any new variables with 100% certainty ('normal' logic OR minecounting logic), THEN guess. This info is directly obtained from 'self.solver', as you can see (`if self.solver.guess`) (2) TESTING TESTING USAGE: if `self.unnecessary_guesses`, then guesses are done -> the lost game missed logic tester in 'constraint_problem_solver_for_testing.py' will notice that missing logic was found, and the 'missing_logic' counter will increase and turn red, proving that it works. Awesome!
        guess(self.solver.guess)                                # you guessed it, it guesses. When 'self.solver.guess' is None, then it performs a not-terrible guess first into corners, then to edges of the map (they have highest chance of being 0, so highest chance of revealing a lot of new information)
    
    ^^ normally the above ensures that a guess is done only when necessary. 
    When 'self.unnecessary_guesses = True', it guesses anyways, 
    even if it already found answers in CSP_solver_old or CSP_solver
    (sidenote: simple_solver will loop as long as it produces solutions, 
    so if it DOES provide solutions, it will return and not go here ever)
    
    (2) run the Minesweeper() with parameter 'unnecessary_guesses = True'. This enables unnecessary guessing
    -> validity testing in 'constraint_problem....py' will find that unnecessary guesses were done,
    proving that validity testing works Perfect! c:

    Minecount demo number: choose 1, 2 or 3 -> demonstrates minecount situations
    '''

    beginner = 9,9,10                   # width, height, mines
    intermediate = 16,16,40
    expert = 30,16,99                   # 480 cells. Expert mine density is 20.625 %. These all have that, just the size differs. Size: 480 cells
    big_expert = 50,24,248              # 1200 cells, 20.666 % mines
    bigger_expert = 60,24,297           # 1440 cells, 20.625 % m.
    BIGGEST_expert = 60,42,520          # 2520 cells, 20.63 % m.
    Humongous_expert = 100,42,866       # 4200 cells, 20.63 % m.
    Sus_Amongus_Expert = 100,50,1031    # 5000 cells, 20.62 % m.

    dense_beg = 9,9,70
    less_dense_beg = 9,9,15
    too_many_mines = 5,5,16
    small_weirdo = 4,4,6
    big_ez = 50,24,200
    
    minecount_demonstration_sometimes = 5,5,15

    ''' ↓↓↓ STARTS A NEW MINESWEEPER with the ability to play the bot by pressing b ↓↓↓ (instructions in the game) '''
    # Minesweeper(beginner, csp_on=False) # IF YOU WANT ONLY simple_solver(), which WORKS at the moment, then use this. It can only solve simple maps where during each turn, it flags all the neighbours if the number of neighbours equals to its label, AND can chord if label = number of surrounding mines.
    #             width      height     mines
    Minesweeper(expert, csp_on=True, 
    minecount_demo_number=None, logic_testing_on=False, unnecessary_guesses=False)