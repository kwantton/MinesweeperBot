import pygame
from random import sample
from constraint import Problem                          # this can be used to solve groups of CSP-equations (CSP = constraint satisfaction problem)
from cell_id_names import flag, unclicked, mine, labellize

# cell = a clickable square of the minesweeper map, 'ruutu'. 'Label' = the id of a cell, like '0' or 'flag'.
class Minesweeper:
    def __init__(self, width, height, mines):
        pygame.init()
        pygame.display.set_caption('MINESWEEPER')
        self.mouse_pos = (0,0)
        self.opened = set()                             # all thus-far opened cells {(x0,y0), (x1,y1),...}, updated when new cells are opened
        self.cells_to_open = width*height - mines

        self.cell_size = 50                             # how many px in height and width should each cell be?
        self.infobar_height = 100                       # pixels for the infobar above the minesweeper map
        self.instructions_height = 150                  # pixels for the instructions bar below the minesweeper map
        self.font = pygame.font.Font(None, 36)
        self.height = height                            # map height measured in in rows
        self.width = width

        self.mines = mines
        if mines >= width*height:
            raise ValueError(f'too many mines, max is {width*height-1} for this size')
        
        self.initialize_debug_features()
        self.images = {}                                # {name : loaded image}
        self.load_images()

        self.screen = pygame.display.set_mode((self.cell_size*width, self.cell_size*height + self.infobar_height + self.instructions_height)) # each .png is 100 px, which is large. Extra height for info bar above the minesweeper map, and instructions bar below the minesweeper map
        self.clock = pygame.time.Clock()
        self.new_game()
        self.loop()

    def initialize_debug_features(self):
        print('\ninitialize_debug_features()')
        self.highlight_front = False                    # 'front' cells = number-labeled cells that neighbour unsolved cells, i.e. cells in x € {1,2,...8} that do not have x flags marked around them. When this is 'True', it draws a yellow rectangle around each such cell.
        self.highlight_bot_location = False

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
        self.inner = set()                  # cells that are not finished and are not neighboured by any opened cells (i.e., are not 'seen' by any opened cells)
        self.opened = set()
        self.started = False                # the mines will be placed AFTER the first click, as in real minesweeper. Otherwise you could lose on the first click. For that, we need to keep track on if the first click has already commenced or not.
        self.victory = False
        self.finished = set()               # cells where label is 0 OR the number of surrounding mines = label
        self.elapsed_time = 0
        self.start_time = None
        self.hit_a_mine = False
        self.timer_active = False
        self.minecount = self.mines
        self.map = [[unclicked for x in range(self.width)] for y in range(self.infobar_height, self.height + self.infobar_height)]   # map = all the mines. Since the infobar is on top, the '0' y for mines = infobar_height. This map records the names of the images of each cell on the map.
        # self.problem = Problem()    # 'constraint satisfaction problem' (CSP) solver class (https://pypi.org/project/python-constraint/). I'm using 'problem.addVariables(list_of_cells, [domain_member_1, domain_member_2,...])' where 'domain' = lähtöjoukko, i.e. the constraints, i.e. the list of accepted values for each variable, i.e. {0,1} in the case of minesweeper. This helps narrowing down the results (I do not know how it's implemented in the class, though!)

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
            elif event.key == pygame.K_q:
                exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(f'MOUSEBUTTONDOWN;')
            mouse_x, mouse_y = pygame.mouse.get_pos()                               # to-do: make a check if it's on a cell, if needed!
            cell_x = mouse_x // self.cell_size
            cell_y = (mouse_y - self.infobar_height) // self.cell_size              # adjust for the infobar ('raise' the click by infobar height), then get the row number by division by self.scale. Asked from ChatGPT when trying to find the problem
            if cell_y < 0 or cell_y > self.cell_size * self.height + self.infobar_height:
                pass                                                                # if you click the top bar, it starts a new game
            elif event.button == 1:                                                 # left click == 2!
                print(f'- cell_x, cell_y: {cell_x, cell_y}')                        # if each cell width is e.g. 100 px, then if you click e.g. on x-coord 540, it's the 6th column (40 would be 1st)
                if not self.started:
                    self.handle_first_left_click(cell_x, cell_y)
                else:
                    self.probe(cell_x, cell_y)
            elif event.button == 3:                                                 # right click == 3!
                self.handle_right_click(cell_x, cell_y)
        elif event.type == pygame.QUIT:
            exit()
    
    def handle_first_left_click(self, x:int, y:int) -> None:
        print('\nhandle_first_left_click()')
        self.start_x = x                                                      # If you click, the start coordinates are where you first click. If you don't click, but instead press b right away to let the bot make the first move, then by default 'self.start_x' = 'self.start_y' = 0 (top left corner of the map).
        self.start_y = y
        self.started = True
        self.start_time = pygame.time.get_ticks()
        self.timer_active = True
        self.generate_map(x, y)
        self.probe(x, y)

    # based on the coordinates of the first clicked cell (mouse_x, mouse_y), place the mines elsewhere
    def generate_map(self, mouse_x:int, mouse_y:int) -> None:
        print('\ngenerate_map()')
        available_coordinates = [(x,y) for y in range(self.height) for x in range(self.width) if (x,y) != (mouse_x, mouse_y)]
        self.mine_locations = set(sample(available_coordinates, self.mines))   # NB! This line of code 'generates' the map by deciding mine locations! This samples a 'self.mines' number of mines (e.g. 99 in an expert game) from 'available_cordinates' which excludes the opening cell that was clicked.
        print(f'- clicked coordinates {mouse_x, mouse_y} and placed the mines as follows:\n', self.mine_locations)

    def probe(self, x:int, y:int) -> None:
        print('\nprobe();')
        print('- entered cell (x,y):', (x, y))

        if self.map[y][x] == unclicked:
            self.handle_opening_a_new_cell(x, y)
        if y >= self.height:                                        # if the lower box is clicked (below the minesweeper map). This has to be written here, or the last elif (self.map[y][x]) will cause an error.
            pass
        elif self.map[y][x] == flag:                                # if you left click on a red flag (i.e. 'probe' a flagged cell), it does nothing (like in real minesweeper)
            pass
        elif (x, y) in self.mine_locations:
            self.map[y][x] = mine
            self.game_over(x,y)
            return
        elif (x, y) in self.opened:
            self.handle_probing_of_already_opened_cell(x,y)         # it's possible that this is a chording, but you can't know that unless you check the number of marked flags around the cell first
            return
        
    def game_over(self, x:int, y:int) -> None:
        print('game_over(): HIT A MINE AT COORDINATES:', (x, y))
        self.hit_a_mine = True
        self.timer_active = False
        self.draw_display()       

    def handle_probing_of_already_opened_cell(self, x:int, y:int) -> None:      # this kind of a probing (when humans play) is either a chording, or a wasted click (it doesn't do anything)
        print('\nhandle_probing_of_already_opened_cell()')
        neighbours = self.neighbours_coordinates(x, y)                          # finds all the actual cells neighbouring (x,y)
        n_surrounding_flags = self.count_flags(neighbours)
        label = self.map[y][x]
        if label == labellize(n_surrounding_flags):
            self.handle_chord(x, y)
    
    def handle_opening_a_new_cell(self, x:int, y:int) -> None:
        print('\nhandle_opening_of_a_new_cell()')
        self.opened.add((x, y))                                                 # why: in case a zero is clicked open, I'm using handle_click recursively to open up all the surrounding cells that are not mines. For that, this list is needed, so that an endless recursion doesn't occur.
        neighbours = self.neighbours_coordinates(x, y)
        
        label = 0
        for neighbour in neighbours:
            if neighbour in self.mine_locations:
                label += 1
        self.map[y][x] = labellize(label)
        if label == 0:                                                  # cells with label '0' are never in 'self.front', as they provide no information that's useful for solving the remaining map (they are the 2nd- or higher order neighbours of unsolved cells)
            for neighbour in neighbours:
                self.probe(neighbour[0], neighbour[1])
        else:
            self.front.add((x,y))                                               # bookkeeping of the current frontline (rintama) of not-yet-solved parts of the map

    def neighbours_coordinates(self, x:int, y:int) -> list:                     # returns a list of tuples [(x1,y1), (x2,y2),...]
        neighbours = [(w,h) for h in range(y-1, y+1+1) for w in range(x-1,x+1+1) if 0<=w<self.width and 0<=h<self.height and (w,h) != (x,y)]    # this returns ALL the neighbours; no matter if 0,1,2,3,4,5,6,7,8,flag,mine,whatever
        return neighbours

    def count_flags(self, neighbours:list) -> int:
        count = 0
        for n in neighbours:
            if self.map[n[1]][n[0]] == flag:
                count += 1
        return count

    def count_cells_of_type(self, counted_cell_type:str, coordinates:list) -> int:
        print(f'\ncount_cells_of_type({counted_cell_type})')
        count = 0
        for c in coordinates:
            if self.map[c[1]][c[0]] == counted_cell_type:
                count += 1
        print('- count:', count)
        return count
    
    def get_cells_of_type(self, wanted_cell_type:str, coordinates:list, negative=False) -> list:
        print(f'\nget_cells_of_type({wanted_cell_type})')
        l = []
        for c in coordinates:
            if negative:
                if self.map[c[1]][c[0]] != wanted_cell_type:
                    l.append(c)    
            else:
                if self.map[c[1]][c[0]] == wanted_cell_type:
                    l.append(c)
        print('- l length:', len(l))
        return l

    def handle_chord(self, x:int, y:int):
        for neighbour in self.neighbours_coordinates(x,y):
            if self.map[neighbour[1]][neighbour[0]] == unclicked:                   # without this, it would chord also flagged cells
                self.probe(neighbour[0], neighbour[1])

    def handle_right_click(self, x:int, y:int):
        if self.map[y][x] == flag:
            self.map[y][x] = unclicked
            self.minecount += 1                                                         # 'minecount' is the number visible on top left of the infobar. It simply is self.mines - 'the Number Of Flags On The Map Currently'
        elif self.map[y][x] == unclicked:
            self.map[y][x] = flag
            self.minecount -= 1

    def bot_act(self) -> None:                                                          # before this, if started with 'b', there's been in order (1) 'self.handle_first_left_click()' (2) 'self.generate_map()' (3) 'self.probe()'
        print('\nbot_act():')                                                           # the following prints will be '- something', '- something_else'. I like this way of console printing because it makes it faster to search for the useful stuff at a given moment in the console, and makes it clear which print originates from which function.

        def brain() -> None:
            obsolete_front = []                                                         # all members of the 'self.front' [(x1,y1), (x2,y2)..] that no longer provide useful information for solving the game; they will be removed later
            print('- brain')
            print(' - self.front size:', len(self.front))
            for x,y in self.front:
                
                label = self.map[y][x]
                neighbours = self.neighbours_coordinates(x,y)                                   # self.bot_x and self.bot_y had been initially set in self.handle_first_left_click as the x (column number) and y (row number) of the first click
                unflagged_unclicked_neighbours = self.get_cells_of_type(unclicked, neighbours)  # this is indeed 'unclicked unflagged neighbours', since label 'unclicked' means exactly that; the picture for 'unclicked' is an unprobed cell. A big confusing perhaps, I know.
                number_of_surrounding_flags = self.count_cells_of_type(flag, neighbours)
                
                if len(unflagged_unclicked_neighbours) + number_of_surrounding_flags == label:
                    print('  - flag_all()')
                    flag_all(unflagged_unclicked_neighbours)
                if label == labellize(number_of_surrounding_flags):                     # If the number of flagged neighbours equals to the label of the current cell,
                    if len(unflagged_unclicked_neighbours) >= 1:                        # if there also are unclicked cells around,
                        self.handle_chord(x,y)                                          # then open all of them (i.e. 'chord').
                    if (x,y) in self.front:                                             # if all the mines have been marked for the current cell (e.g. 3 flags around a cell with label 3) and the cell has been chorded, then remove that cell from the front, as it no longer provides useful information.
                        obsolete_front.append((x,y))
            for coordinate in obsolete_front:                                           # why not remove them right away? Because you can't remove an item from an iterable while it's being iterated over, otherwise, in this case, you'll get 'RuntimeError: Set changed size during iteration'
                self.front.remove(coordinate)

        def flag_all(cells) -> None:
            for cell in cells:
                x,y = cell[0], cell[1]
                if self.map[y][x] == unclicked:
                    self.map[cell[1]][cell[0]] = flag
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
            if self.timer_active:
                current_time = pygame.time.get_ticks()
                self.elapsed_time = (current_time - self.start_time) / 1000 
            timer_surface = self.font.render(f'Time: {self.elapsed_time}', True, (255,255,255))             # 'self.elapsed_time' is 0 by default
            self.screen.blit(timer_surface, (10, 50)) 
        
        def draw_victory() -> None:
            victory_surface = self.font.render(f'MAP CLEARED!', True, (0,255,0))
            self.screen.blit(victory_surface, (self.cell_size*self.width-200, 10))
        
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
        
        def highlight_bot_blue() -> None:
            surface = transparent_highlight_surface(0,0,255,128)
            self.screen.blit(surface, (self.start_x*self.cell_size, self.start_y*self.cell_size + self.infobar_height))
        
        def draw_map() -> None:
            for x in range (self.width):
                for y in range(self.height):
                    cell_status = self.map[y][x]                                                    # self.map is a list of lists; indices start from 0
                    self.screen.blit(source=self.images[cell_status], dest=(x*self.cell_size, y*self.cell_size+self.infobar_height))
        
        def draw_instructions_bar() -> None:
            instructions = 'b = bot move  f = front highlighting  l = bot start location  spacebar = new game'.split('  ')  # this is used a lot on the 'Data analysis with Python' cours, it's very handy for making lists quickly. This splits at each double space (two spaces in a row)
            start_y = self.height * self.cell_size + self.infobar_height + 10
            for i, instruction in enumerate(instructions):                                          # it isn't possible to use a multiline text, so each instruction has to be drawn separately. For this solution, I asked ChatGPT.
                instruction_surface = self.font.render(instruction, True, (255,255,255))
                self.screen.blit(instruction_surface, (10, start_y + i * 30))                       # draw all the instructions beneath each other
        
        if self.victory:
            draw_victory()
        elif self.hit_a_mine:
            draw_hit_a_mine()
        
        draw_minecount()
        draw_timer()
        draw_map()
        draw_instructions_bar()
        if self.highlight_front:
            highlight_front_cells_yellow()
        if self.highlight_bot_location:
            highlight_bot_blue()
        pygame.display.flip()                                               # display.flip() will update the contents of the entire display. display.update() enables updating of just a part IF you specify which part
        self.clock.tick(30)
    
    def loop(self) -> None:
        while True:                                                         # I'm enabling continuing after hitting a mine as well
            self.is_map_cleared()
            for event in pygame.event.get():
                self.inspect_event(event)
            self.draw_display()                                             # (2) then draw the screen after handling them

if __name__ == '__main__':
    dense_beg = 9,9,70
    beginner = 9,9,10
    intermediate = 16,16,40
    expert = 30,16,99           
    Minesweeper(beginner[0], beginner[1], beginner[2])          # width, height, mines