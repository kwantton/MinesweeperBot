import pygame
from random import sample
from constraint import Problem                          # this can be used to solve groups of CSP-equations (CSP = constraint satisfaction problem)
from CSP_solver import CSP_solver, format_equation_for_csp_solver
from cell_id_names import flag, unclicked, mine, safe, labellize, read_number_from_label

# cell = a clickable square of the minesweeper map, 'ruutu'. 'Label' = the id of a cell, like '0' or 'flag'.
class Minesweeper:
    def __init__(self, width, height, mines, csp_on=True, debug_csp=False):
        pygame.init()
        pygame.display.set_caption('MINESWEEPER')
        self.cells_to_open = width*height - mines
        
        # NB! Put here ONLY those that are not reset at every 'new_game()'
        self.mines = mines
        self.width = width
        self.cell_size = 50-int(0.8*height)             # how many px in height and width should each cell be?
        self.csp_on = csp_on
        self.height = height                            # map height measured in rows
        self.infobar_height = 100                       # pixels for the infobar above the minesweeper map
        self.debug_csp = debug_csp
        self.clock = pygame.time.Clock()
        self.initialize_debug_features()
        self.font = pygame.font.Font(None, 36-int(0.5*height))
        
        if mines >= width*height:
            raise ValueError(f'too many mines, max is {width*height-1} for this size')
        
        self.images = {}                                # {name : loaded image}
        self.load_images()
        self.screen = pygame.display.set_mode((self.cell_size*width, self.cell_size*height + self.infobar_height + self.instructions_height), pygame.RESIZABLE) # each .png is 100 px, which is large. Extra height for info bar above the minesweeper map, and instructions bar below the minesweeper map
        
        self.new_game()
        self.loop()

    def initialize_debug_features(self):
        print('\ninitialize_debug_features()')
        self.show_mines = False
        self.highlight_front = False                                                # 'front' cells = number-labeled cells that neighbour unsolved cells, i.e. cells in x € {1,2,...8} that do not have x flags marked around them. When this is 'True', it draws a yellow rectangle around each such cell.
        self.highlight_bot_location = False
        self.highlight_csp_solved = self.debug_csp
        self.instructions = '''
        b : bot move
        f : front highlighting
        c : highlight csp-solved cells
        spacebar : new game
        m : show mine locations
        q: quit'''.split('\n        ')                                              # This way of writing lists is used a lot on the 'Data analysis with Python' course, it's very handy for writing longer lists quickly. This splits at each '\n        ' to form a list.
        self.instructions_height = 20 + len(self.instructions)*30                   # pixels for the instructions bar below the minesweeper map

    def load_images(self):
        print('\nload_images')
        image_names = ['images/' + name + '.png' for name in '0 1 2 3 4 5 6 7 8 flag mine unclicked has_to_have_a_mine safe'.split()]
        for image_name in image_names:
            self.images[image_name] = pygame.transform.scale(pygame.image.load(image_name), (self.cell_size,self.cell_size))

    def new_game(self):                     # i.e. initialize all variables
        print('\n-----------------------------')
        print("NEW_GAME")
        self.start_x = 0
        self.start_y = 0
        self.front = set()                  # cells that are not finished
        self.inner = set()                  # cells that are not finished and are not neighboured by any opened cells (i.e., are not 'seen' by any opened cells). TO-DO; I haven't touched these yet; these come into play when I start handling guesses
        self.opened = set()                 # all thus-far opened cells {(x0,y0), (x1,y1),...}, updated when new cells are opened

        self.started = False                # the mines will be placed AFTER the first click, as in real minesweeper. Otherwise you could lose on the first click. For that, we need to keep track on if the first click has already commenced or not.
        self.victory = False
        self.finished = set()               # cells where label is 0 OR the number of surrounding mines = label
        self.current_time = 0
        self.elapsed_time = 0
        self.mouse_pos = (0,0)
        self.start_time = None
        self.hit_a_mine = False
        self.timer_active = False
        self.obsolete_front = set()         # after each legitimate chording, and after entering a new previously unprobed cell if it has no neighbours
        self.new_front_members = set()
        self.solver = CSP_solver(mines_total = self.mines)                          # minecount is needed in 'CSP_solver' in those rarish cases where information about the remaining minecount near the end of the game is needed to be able to solve the last few cases that would otherwise require guessing.
        
        self.minecount = self.mines
        self.previous_round_minecount = -1                                          # inspect: if current minecount == previous, then try minecount logic. Then if that doesn't work, try quessing (last resort)

        self.map = [[unclicked for x in range(self.width)] for y in range(self.infobar_height, self.height + self.infobar_height)]   # map = all the mines. Since the infobar is on top, the '0' y for mines = infobar_height. This map records the names of the images of each cell on the map.

    def inspect_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:                                         # event.key, not event.type, sigh. I was looking for this with cats and dogs
                self.new_game()
            elif event.key == pygame.K_b:                                           # BOT:
                if not self.started:
                    self.handle_first_left_click(self.start_x, self.start_y)
                self.bot_act()                                                      # the bot makes a move when you press b
            elif event.key == pygame.K_f:
                self.highlight_front = not self.highlight_front                     # toggle debug; highlighting the frontline (rintama) of not-yet-solved portion of the map, on/off toggle
            elif event.key == pygame.K_l:
                self.highlight_bot_location = not self.highlight_bot_location       # toggle debug: highlighting the bot 'location' on/off toggle
            elif event.key == pygame.K_m:
                self.show_mines = not self.show_mines
            elif event.key == pygame.K_c:
                self.highlight_csp_solved = not self.highlight_csp_solved
            elif event.key == pygame.K_q:
                exit()
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
        print('\nhandle_first_left_click()')
        self.start_x = x                                                            # If you click the map in the beginning, the start coordinates are where you first click. If you don't click, but instead press b right away to let the bot make the first move, then by default 'self.start_x' = 'self.start_y' = 0 (top left corner of the map).
        self.start_y = y
        self.started = True
        self.start_time = pygame.time.get_ticks()
        self.timer_active = True
        self.generate_map(x, y)
        self.probe(x, y, primary=True)

    # based on the coordinates of the first clicked cell (mouse_x, mouse_y), place the mines elsewhere
    def generate_map(self, mouse_x:int, mouse_y:int) -> None:
        print('\ngenerate_map()')
        available_coordinates = [(x,y) for y in range(self.height) for x in range(self.width) if (x,y) != (mouse_x, mouse_y)]
        self.mine_locations = set(sample(available_coordinates, self.mines))   # NB! This line of code 'generates' the map by deciding mine locations! This samples a 'self.mines' number of mines (e.g. 99 in an expert game) from 'available_cordinates' which excludes the opening cell that was clicked.
        print(f'- clicked coordinates {mouse_x, mouse_y} and placed the mines as follows:\n', self.mine_locations)

    def probe(self, x:int, y:int, primary=False) -> None:           # if primary = False, then don't go to 'handle_probing_of_already_opened_cell', otherwise it can loop and cause another chord! The chording is meant ONLY for actual chording
        # print(f'\nprobe({x,y}, from primary={primary});')

        if self.map[y][x] == flag:                                  # NB! This has to come first, as this is most probably in 'self.mine_locations'; If you left click on a red flag (i.e. 'probe' a flagged cell), it does nothing (like in real minesweeper)
            return
        elif (x, y) in self.mine_locations:                         # NB! This has to come before the 'unclicked' check; otherwise the next would be true, as all mine-containing cells are 'unclicked' (the tile's name is 'unclicked'!) before clicking c:
            self.map[y][x] = mine
            self.game_over(x,y)
            return
        elif self.map[y][x] == unclicked:
            self.handle_opening_a_new_cell(x, y)                    # this also adds the (x,y) to 'self.opened', which is needed to recognize victory, and for the 'if' clause below.
        elif (x, y) in self.opened and primary:
            # only if 'probe()' was not called from 'chord()'!
            self.handle_probing_of_already_opened_cell(x,y)         # it's possible that this is a chording, but you can't know that unless you check the number of marked flags around the cell first

    def game_over(self, x:int, y:int) -> None:
        print('game_over(): HIT A MINE AT COORDINATES:', (x, y))
        self.hit_a_mine = True
        self.timer_active = False
        self.draw_display()       

    def handle_probing_of_already_opened_cell(self, x:int, y:int) -> None:      # this kind of a probing (when humans play) is either a chording, or a wasted click (it doesn't do anything)
        # print('\nhandle_probing_of_already_opened_cell()')
        neighbours = self.get_neighbours_of(x, y)                               # finds all the actual cells neighbouring (x,y)
        n_surrounding_flags = self.count_flags(neighbours)
        label = self.map[y][x]
        if label == labellize(n_surrounding_flags):
            self.handle_chord(x, y)
        else:
            pass

    def handle_opening_a_new_cell(self, x:int, y:int) -> None:                  # ALL NEW CELL OPENINGS GO HERE, doesn't matter how the cell was opened (player/bot/single click/chord)
        # print('\nhandle_opening_of_a_new_cell()')
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
            # self.front.add((x,y))                                             # bookkeeping of the current frontline (rintama) of not-yet-solved parts of the map
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
        if self.map[y][x] == flag:
            self.map[y][x] = unclicked
            self.minecount += 1                                                         # 'minecount' is the number visible on top left of the infobar. It simply is self.mines - 'the Number Of Flags On The Map Currently'
        elif self.map[y][x] == unclicked:
            self.map[y][x] = flag
            self.minecount -= 1

    def bot_act(self) -> None:                                                          # before this, if started with 'b', there's been in order (1) 'self.handle_first_left_click()' (2) 'self.generate_map()' (3) 'self.probe()'
        # print('\nbot_act():')                                                           # the following prints will be '- something', '- something_else'. I like this way of console printing because it makes it faster to search for the useful stuff at a given moment in the console, and makes it clear which print originates from which function.
        
        width = self.width
        height = self.height
        
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

            # NB! This is the most straightforward way of removing obsolete front cells from 'self.front' in one go. For each cell in 'self.front', it checks if it has unclicked neighbours. If not, it removes all those cells from 'self.front'. Previously, I had this whole functionality split up into subcases: chording cases and cases of entering a new cell, but that serves no actual purpose, it's too complicated, error-prone and doesn't really save processing (almost) at all. This is much better, universal, reusable and clearer, and is utilized by the CSP-bot as well too. This function is for ensuring that there DEFINITELY are no obsolete front cells in self.front any longer, as that has been my problem for days now.
            def filter_front_cells():
                add_new_front_cells_to_self_front()                                         # I switched the order of 'add_new..' and 'remove_obsolete...' around; the only way to make absolutely sure that no obsolete front survives the filtering is to (1) FIRST add the new self.front members and (2) from THESE ALSO, filter out the unneeded ones (obsolete ones).
                for x,y in self.front:
                    neighbours = self.get_neighbours_of(x, y)
                    n_unclicked_unflagged_neighbours = self.count_cells_of_type(unclicked, neighbours)
                    if n_unclicked_unflagged_neighbours == 0:
                        if (x,y) in self.front:
                            self.obsolete_front.add((x,y))
                remove_obsolete_front()

            def check_minecount_zero():
                if self.minecount == 0:
                    for x in range (width):
                        for y in range (height):
                            if self.map[y][x] == labellize('unclicked'):
                                self.probe(x,y,True)
            
            def check_for_stalling():
                all_unclicked = []
                need_for_minecount = False
                if self.minecount == self.previous_round_minecount:                                             # don't waste resources going through the whole map below (not terrible, but not needed. Also expert has 480 cells; don't go through them all if you don't have to) if the minecount keeps steadily decreasing; i.e., if minecount is not needed, don't use it, use 'normal' logic
                    if self.minecount < 10:
                        need_for_minecount = True
                        for x in range (width):
                            for y in range (height):
                                if self.map[y][x] == labellize('unclicked'):
                                    all_unclicked.append((x,y))                
                self.previous_round_minecount = self.minecount                                                  # update for the next round, based on the current minecount
                return need_for_minecount, all_unclicked
            
            # this function's "for x,y in self.front" loop finds SIMPLE non-CSP solutions: (1) where the number of neighbouring unflagged unclicked cells + flagged cells equals to the label -> flag all, and (2) if label = number of surrounding flags, then perform a chord. Then, I remove unnecessary cells from the front to cut unnecessary computing work for the linear equation CSP solver.
            def simple_solver() -> None:    
                for x,y in self.front:
                    label = self.map[y][x]    
                    neighbours = self.get_neighbours_of(x,y)                                                    # self.bot_x and self.bot_y had been initially set in self.handle_first_left_click as the x (column number) and y (row number) of the first click
                    number_of_surrounding_flags = self.count_cells_of_type(flag, neighbours)
                    unflagged_unclicked_neighbours = self.get_cells_of_type(unclicked, neighbours)              # this is indeed 'unclicked unflagged neighbours', since label 'unclicked' means exactly that; the picture for 'unclicked' is an unprobed cell. A big confusing perhaps, I know.

                    if label == labellize(len(unflagged_unclicked_neighbours) + number_of_surrounding_flags):   # If the number of surrounding ('unclicked' + 'flag') cells equals to the label of this (x,y) front cell in question (for example, 1 flagged + 2 unclicked = 3 = the label of the cell),
                        flag_these(unflagged_unclicked_neighbours)                          # then flag the remaining unflagged cells around the front cell in question (flag the remaining 2 unclicked cells in this example case).

                    # At this point, I COULD update the 'number_of_surrounding_flags' again, since I just (potentially) placed new flags above. If I updated the number of surrounding flags here, the benefit would be a chance for the 'if' clause below to enable performing a chord already during this round instead of during the next round of simple_solver(). However, it's visually much better and clearer to proceed one step at a time, instead of chording below right away; it helps in debugging, and looks a lot nicer when looking at the bot doing its job one small step at a time.

                    if label == labellize(number_of_surrounding_flags):                     # NB! 'if', not 'elif'. If the number of flagged neighbours equals to the label of the current front cell,
                        if len(unflagged_unclicked_neighbours) >= 1:                        # then if there also are unclicked cells around the current front cell,
                            self.handle_chord(x,y)                                          # then open all of them (i.e. 'chord' at this current front cell (x,y)).
                
                check_minecount_zero()                                                      # if minecount is zero, then probe all 'unclicked' cells, since they cannot be mines -> map completed! This situation needs separate handling because the last 'unclicked' cells can be inside completely flagged boxes, isolating them from 'self.front'. It took me 5 weeks to even arrive in that kind of a situation! It's extremely rare, as it needs at least 3 already-flagged cells in a cordner, or 5 in a center edge, or 8 or more in the middle! Awesomesauce.
                filter_front_cells()

            simple_solver()

            # if I don't 'draw_display()' here, when using debugger, I wouldn't be able to see the map before csp-section code is executed c:
            if self.debug_csp:
                self.draw_display()

            # after removing thus far redundant cells from the 'self.front' (done in 'update_front'), I'm feeding equations into my CSP linear equation solver:
            def feed_csp_solver():
                csp_solver_input = []                                                                   # a list of lists; [ [x, y, ('var_a', 'var_b', 'var_c', ...), label_of_cell], [...], ...]; each inner list represents a set of (1) (x,y), (2) variables to try to solve (cells, which can have value 0 or 1), (3) the total number of mines (sum) of those variables
                for x,y in self.front:
                    surrounding_mine_count = read_number_from_label(self.map[y][x])                     # all 'self.front' cells have number labels, number = 1,...8 (not 0). It cannot be 0, since we just removed those cells from 'self.front' in the 'for...' loop above
                    neighbours = self.get_neighbours_of(x,y)
                    unflagged_unclicked_neighbours = self.get_cells_of_type(unclicked, neighbours)
                    n_surrounding_flags = self.count_flags(neighbours)
                    csp_solver_input_addition = format_equation_for_csp_solver(x, y, unflagged_unclicked_neighbours, surrounding_mine_count - n_surrounding_flags)    # NB! 'surrounding_mine_count - n_surrounding_flags' was what I was missing for two days; it caused solving of WRONG equations in the CSP_solver(). I.e.; what if there are flags around, not just unflagged neighbours? That's why there's the '- n_unflagged_neighbours' subtraction. They have to be removed from the total minecount.
                    csp_solver_input.append(csp_solver_input_addition)
                self.solver.handle_incoming_equations(csp_solver_input)

            if self.debug_csp:
                self.draw_display()

            feed_csp_solver()

            def csp_solve():
                need_for_minecount, all_unclicked_cells = check_for_stalling()
                self.solver.absolut_brut(self.minecount, need_for_minecount, all_unclicked_cells)
                solved_vars = self.solver.solved_variables      # each is a tuple ((x,y), value)
                print('csp_solve():')
                # print('-solved_vars:', solved_vars)
                for (x,y), value in solved_vars:
                    # print(f'- solved {x,y} = {value}')
                    if value == 1:
                        flag_these([(x,y)])
                    elif value == 0:                            
                        self.handle_opening_a_new_cell(x, y)    # NB! 'handle_opening_a_new_cell' adds new front members to 'self.new_front_members', NOT yet to self.front, to avoid 'Set changed size during iteration', since 'handle_opening_a_new_cell' was originally used in 'simple_solver' which iterates over 'self.front' and thus cannot directly modify 'self.front' while iterating over it without causing the error.
                        # TO-DO; now, via utilizing handle_opening_a_new_cell, obsolete front should be added from there correctly.
                filter_front_cells()                            # TO-DO: for this to work, the 'self.front' has to be kept up-to-date. That works; it's done in 'flag_these()' and in 'handle_opening_a_new_cell()' above.
                # print('- solved_vars:', solved_vars)
            
            if self.csp_on:
                csp_solve()

        def flag_these(cells) -> None:              # NB! this ensures that a flag is placed in all, only when appropriate
            for x,y in cells:
                if self.map[y][x] == unclicked:     # NB! this ensures that a flag is placed in all, only when appropriate
                    self.toggle_flag(x,y)
        
        brain()
    
    def is_map_cleared(self) -> None:
        if len(self.opened) == self.cells_to_open:
            self.victory = True
            self.timer_active = False

    def draw_display(self) -> None:
        self.screen.fill((0,0,0))

        def draw_minecount() -> None:
            minecount_surface = self.font.render(f'Mines left: {self.minecount}', True, (255,255,255))      # True is for antialiasing. White is 255,255,255
            self.screen.blit(minecount_surface, (10,10))
        
        def draw_timer() -> None:
            if self.timer_active :
                self.current_time = pygame.time.get_ticks()
                self.elapsed_time = (self.current_time - self.start_time) / 1000 
                shown_time = f'{((self.current_time - self.start_time) // 1000):.0f}'
            elif not self.started:
                shown_time = 0
            else:
                shown_time = f'{self.elapsed_time:.3f}'                                                 # after clearing the map, show exact time
            timer_surface = self.font.render(f'Time: {shown_time}', True, (255,255,255))                # 'self.elapsed_time' is 0 by default
            self.screen.blit(timer_surface, (10, 50)) 
        
        def draw_victory() -> None:
            if not self.hit_a_mine:
                text = 'MAP CLEARED!'
                y = 10
                x = self.cell_size*self.width-200
            else:
                text = '.. and completed'
                y = 50
                x = self.cell_size*self.width-230
            victory_surface = self.font.render(text, True, (0,255,0))
            self.screen.blit(victory_surface, (x, y))
        
        def draw_hit_a_mine() -> None:
            hit_a_mine_surface = self.font.render(f'HIT A MINE!', True, (255,0,0))
            self.screen.blit(hit_a_mine_surface, (self.cell_size*self.width-200, 10))
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
        
        def highlight_start_location_blue() -> None:
            surface = transparent_highlight_surface(0,0,255,128)
            self.screen.blit(surface, (self.start_x*self.cell_size, self.start_y*self.cell_size + self.infobar_height))

        def highlight_csp_solved() -> None:
            mine_surface = transparent_highlight_surface(255,0,0,128)
            safe_surface = transparent_highlight_surface(0,255,0,128)
            for (x,y), mine in self.solver.solved_variables:
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
        
        def draw_map() -> None:
            for x in range (self.width):
                for y in range(self.height):
                    cell_status = self.map[y][x]                                                    # self.map is a list of lists; indices start from 0
                    self.screen.blit(source=self.images[cell_status], dest=(x*self.cell_size, y*self.cell_size+self.infobar_height))
        
        def draw_instructions_bar() -> None:
            start_y = self.height * self.cell_size + self.infobar_height + 10
            for i, instruction in enumerate(self.instructions):                                          # it isn't possible to use a multiline text, so each instruction has to be drawn separately. For this solution, I asked ChatGPT.
                instruction_surface = self.font.render(instruction, True, (255,255,255))
                self.screen.blit(instruction_surface, (10, start_y + i * 30))                       # draw all the instructions beneath each other
        
        if self.victory:
            draw_victory()
        if self.hit_a_mine:                                                                         # I'm enabling both, in case someone wants to try to finish it still
            draw_hit_a_mine()
        
        draw_minecount()
        draw_timer()
        draw_map()
        draw_instructions_bar()
        if self.highlight_front:
            highlight_front_cells_yellow()
        if self.highlight_bot_location:
            highlight_start_location_blue()
        if self.show_mines:
            highlight_mines_red()
        if self.highlight_csp_solved:
            highlight_csp_solved()
        pygame.display.flip()                                               # display.flip() will update the contents of the entire display. display.update() enables updating of just a part IF you specify which part
        self.clock.tick(30)
    
    def loop(self) -> None:
        while True:                                                         # I'm enabling continuing after hitting a mine as well
            self.is_map_cleared()
            for event in pygame.event.get():
                self.inspect_event(event)
            self.draw_display()                                             # (2) then draw the screen after handling them

if __name__ == '__main__':
    beginner = 9,9,10
    intermediate = 16,16,40
    expert = 30,16,99
    dense_beg = 9,9,70
    less_dense_beg = 9,9,15

    ''' ↓↓↓ STARTS A NEW MINESWEEPER with the ability to play the bot by pressing b ↓↓↓ (instructions in the game) '''
    # Minesweeper(beginner[0], beginner[1], beginner[2], csp_on=False) # IF YOU WANT ONLY simple_solver(), which WORKS at the moment, then use this. It can only solve simple maps where during each turn, it flags all the neighbours if the number of neighbours equals to its label, AND can chord if label = number of surrounding mines.
    Minesweeper(expert[0], expert[1], expert[2], csp_on=True) # this one utilizes also csp-solver, which is partially broken at the moment, causing mislabeling of things
    #           width       height      mines