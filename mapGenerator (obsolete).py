import pygame
from random import sample

# cell = a square of the map

class Minesweeper:
    def __init__(self, width, height, mines):
        pygame.init()
        pygame.display.set_caption('MINESWEEPER')
        self.mouse_pos = (0,0)
        self.opened = set()     # all seen zero-cells are gathered here {(x0,y0), (x1,y1),...}
        self.to_open = width*height - mines

        self.scale = 50         # how many px in height and width should each cell be?
        self.infobar = 100      # pixels above the actual map
        self.font = pygame.font.Font(None, 36)
        self.height = height    # map height measured in in rows
        self.width = width

        self.mines = mines
        if mines >= width*height:
            raise ValueError(f'too many mines, max is {width*height-1} for this size')

        self.images = {}        # {name : loaded image}
        self.load_images()

        self.screen = pygame.display.set_mode((self.scale*width, self.scale*height + self.infobar)) # each .png is 100 px, which is large. Extra height for info bar above the actual map
        self.clock = pygame.time.Clock()
        self.new_game()
        self.loop()

    def load_images(self):
        print('\nload_images')
        image_names = ['images/' + name + '.png' for name in '0 1 2 3 4 5 6 7 8 flag mine unclicked has_to_have_a_mine safe'.split()]
        for image_name in image_names:
            self.images[image_name]=pygame.transform.scale(pygame.image.load(image_name), (self.scale,self.scale))

    def new_game(self):
        print("\nnew_game")
        self.started = False                                                        # the mines will be placed AFTER the first click, as in real minesweeper. Otherwise you could lose on the first click. For that, we need to keep track on if the first click has already commenced or not.
        self.victory = False
        self.hit_a_mine = False
        self.minecount = self.mines
        self.opened = set()
        self.start_time = None
        self.timer_active = False
        self.elapsed_time = 0
        self.map = [['images/unclicked.png' for x in range(self.width)] for y in range(self.infobar, self.height+self.infobar)]   # the visuals; names of the images of each cell!

    def inspect_event(self, event):
        #self.mouse_tracker()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:                                         # event.key, not event.type, sigh. I was looking for this with cats and dogs
                self.new_game()
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f'inspect_event(); MOUSEBUTTONDOWN;')
            mouse_x, mouse_y = pygame.mouse.get_pos()                               # to-do: make a check if it's on a cell, if needed!
            mouse_x //= self.scale
            mouse_y = (mouse_y - self.infobar)//self.scale                          # adjust for the infobar ('raise' the click by infobar height), then get the row number by division by self.scale. Asked from ChatGPT when trying to find the problem
            if mouse_y < 0:
                self.new_game()                                                     # if you click the top bar, it starts a new game
            elif event.button == 1:                                                   # left click == 2!
                print(f'- mouse_x//scale, mouse_y//scale: {mouse_x, mouse_y}')      # if each cell width is e.g. 100 px, then if you click e.g. on x-coord 540, it's the 6th column (40 would be 1st)
                if not self.started:
                    self.handle_first_left_click(mouse_x, mouse_y)
                else:
                    self.handle_left_click(mouse_x, mouse_y)
            elif event.button == 3:                                                 # right click == 3!
                self.handle_right_click(mouse_x, mouse_y)
        if event.type == pygame.QUIT:
            exit()

    def mouse_tracker(self):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos != self.mouse_pos:
            x, y = mouse_pos
            print('mouse tracker;')
            print('- x//self.scale, y//self.scale:', x//self.scale, y//self.scale)
            self.mouse_pos = mouse_pos
    
    def handle_first_left_click(self, mouse_x, mouse_y):
        print("\nhandle_first_left_click();")
        self.started = True
        self.start_time = pygame.time.get_ticks()
        self.timer_active = True

        # based on which cell was clicked, place the mines (do not place a mine in the cell that was just clicked)
        self.available_coordinates = [(x,y) for y in range(self.height) for x in range(self.width) if (x,y) != (mouse_x, mouse_y)]
        self.mine_locations = set(sample(self.available_coordinates,self.mines))
        print(f'- clicked coordinates {mouse_x, mouse_y} and placed the mines as follows:\n', self.mine_locations)
        self.handle_left_click(mouse_x, mouse_y)

    def handle_left_click(self, x, y):
        print('\nhandle_click();')
        print('- mouse_x, mouse_y:', (x, y))
        neighbours = self.neighbours_coordinates(x, y)  # finds all the actual surrounding cells

        if (x, y) in self.mine_locations:
            print('- HIT A MINE AT COORDINATES:', (x, y))
            self.map[y][x] = 'images/mine.png'
            self.hit_a_mine = True
            self.timer_active = False
            self.draw_display()
            return
        elif self.map[y][x] == 'images/flag.png':   # if you left click on a flag, it does nothing
            return
        elif (x, y) in self.opened:
            print('- OPEN ALREADY')
            
            flag_count = self.count_surrounding_flags(neighbours)
            label = self.map[y][x]
            if f'images/{flag_count}.png' == label:
                self.handle_chord(x, y)
            return
        else:
            self.opened.add((x, y))                 # why: in case a zero is clicked open, I'm using handle_click recursively to open up all the surrounding cells that are not mines. For that, this list is needed, so that an endless recursion doesn't occur.
            
            label = 0
            for neighbour in neighbours:
                if neighbour in self.mine_locations:
                    label += 1
            self.map[y][x] = f'images/{label}.png'
            if label == 0:
                for neighbour in neighbours:
                    self.handle_left_click(neighbour[0], neighbour[1])
                # TO-DO: POISTA? self.handle_adjacent_zeros(mouse_x, mouse_y, neighbours)        # So, this clicked cell was '0', therefore  in case an adjacent zero is found, all the zeros next to it should also be opened, and all the cells next to all the zeros as well!
        
    def neighbours_coordinates(self, x, y):
        neighbours = [(w,h) for h in range(y-1, y+1+1) for w in range(x-1,x+1+1) if 0<=w<self.width and 0<=h<self.height and (w,h) != (x,y)]
        return neighbours
        # print('\nsourrounding_cells_coordinates():', neighbours)

    def count_surrounding_flags(self, neighbours):
        count = 0
        for n in neighbours:
            if self.map[n[1]][n[0]] == 'images/flag.png':
                count += 1
        return count
    
    def handle_chord(self, x, y):
        for neighbour in self.neighbours_coordinates(x,y):
            if self.map[neighbour[1]][neighbour[0]] == 'images/unclicked.png':  # without this, it would chord also flagged cells
                self.handle_left_click(neighbour[0], neighbour[1])

    def handle_right_click(self, x, y):
        if self.map[y][x] == 'images/flag.png':
            self.map[y][x] = 'images/unclicked.png'
            self.minecount += 1
        elif self.map[y][x] == 'images/unclicked.png':
            self.map[y][x] = 'images/flag.png'
            self.minecount -= 1

    def draw_display(self):
        self.screen.fill((0,0,0))
        minecount_surface = self.font.render(f'Mines left: {self.minecount}', True, (255,255,255))    # True is for antialias, white is 255
        victory_surface = self.font.render(f'MAP CLEARED!', True, (0,255,0))
        hit_a_mine_surface = self.font.render(f'HIT A MINE!', True, (255,0,0))
        if self.timer_active:
            current_time = pygame.time.get_ticks()
            self.elapsed_time = (current_time - self.start_time) / 1000 
        self.screen.blit(minecount_surface, (10,10))
        if self.victory:
            # self.screen.blit(victory_surface, (self.width-100, 10))
            self.screen.blit(victory_surface, (self.scale*self.width-200, 10))
        elif self.hit_a_mine:
            self.screen.blit(hit_a_mine_surface, (self.scale*self.width-200, 10))
        timer_surface = self.font.render(f'Time: {self.elapsed_time}', True, (255,255,255))
        self.screen.blit(timer_surface, (10, 50)) 
        for x in range (self.width):
            for y in range(self.height):
                cell_status = self.map[y][x]    # self.map is a list of lists; indices start from 0
                self.screen.blit(source=self.images[cell_status], dest=(x*self.scale, y*self.scale+self.infobar))
        
        pygame.display.flip()   # display.flip() will update the contents of the entire display. display.update() enables updating of just a part IF you specify which part
        self.clock.tick(30)
    
    def map_cleared_check(self):
        if len(self.opened) == self.to_open:
            self.victory = True
            self.timer_active = False
    
    def loop(self):
        while True:
            self.map_cleared_check()
            for event in pygame.event.get():
                self.inspect_event(event)
            self.draw_display()                                 # (2) then draw the screen after handling them

if __name__ == '__main__':
    beginner = 9,9,10
    intermediate = 16,16,40
    expert = 30,16,99           # width, height, mines
    Minesweeper(expert[0], expert[1], expert[2])