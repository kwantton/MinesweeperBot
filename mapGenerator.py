import pygame
from random import sample

# cell = a square of the map

class Minesweeper:
    def __init__(self, width, height, mines):
        pygame.init()
        self.mouse_pos = (0,0)
        self.opened = set()      # all seen zero-cells are gathered here {(x0,y0), (x1,y1),...}

        self.scale = 50         # how many px in height and width should each cell (image) be?
        self.height = height    # map height measured in in rows
        self.width = width

        self.mines = mines
        if mines >= width*height:
            raise ValueError(f'too many mines, max is {width*height-1} for this size')

        self.images = {}        # {name : loaded image}
        self.load_images()

        self.screen = pygame.display.set_mode((self.scale*width, self.scale*height)) # each .png is 100 px, which is large.
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
        self.map = [['images/unclicked.png' for x in range(self.width)] for y in range(self.height)]   # the visuals; names of the images!

    def inspect_event(self, event):
        #self.mouse_tracker()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()                               # to-do: make a check if it's on a cell, if needed!
            print(f'inspect_event(): MOUSEBUTTONDOWN;')
            print(f'- mouse_x//scale, mouse_y//scale: {mouse_x//self.scale, mouse_y//self.scale}')  # if each cell width is e.g. 100 px, then if you click e.g. on x-coord 540, it's the 6th column (40 would be 1st)
            if not self.started:
                self.handle_first_click(mouse_x//self.scale, mouse_y//self.scale)
            else:
                self.handle_click(mouse_x//self.scale, mouse_y//self.scale)
        if event.type == pygame.QUIT:
            exit()

    def mouse_tracker(self):
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pos != self.mouse_pos:
            x, y = mouse_pos
            print('mouse tracker;')
            print('- x//self.scale, y//self.scale:', x//self.scale, y//self.scale)
            self.mouse_pos = mouse_pos
    
    def handle_first_click(self, mouse_x, mouse_y):
        print("\nhandle_first_click();")
        self.started = True

        # based on which cell was clicked, place the mines (do not place a mine in the cell that was just clicked)
        self.available_coordinates = [(x,y) for y in range(self.height) for x in range(self.width) if (x,y) != (mouse_x, mouse_y)]
        self.mine_locations = set(sample(self.available_coordinates,self.mines))
        print(f'- clicked coordinates {mouse_x, mouse_y} and placed the mines as follows:\n', self.mine_locations)
        self.handle_click(mouse_x, mouse_y)

    def handle_click(self, mouse_x, mouse_y):
        print('\nhandle_click();')
        if (mouse_x, mouse_y) in self.opened:
            print('- WAS OPEN ALREADY')
            return
        self.opened.add((mouse_x, mouse_y))                 # why: in case a zero is clicked open, I'm using handle_click recursively to open up all the surrounding cells that are not mines. For that, this list is needed, so that an endless recursion doesn't occur.
        print('- mouse_x, mouse_y:', (mouse_x, mouse_y))
        if (mouse_x, mouse_y) in self.mine_locations:
            print('- HIT A MINE AT COORDINATES:', (mouse_x, mouse_y))
            self.map[mouse_y][mouse_x] = 'images/mine.png'
        else:
            neighbours = self.surrounding_cells_coordinates(mouse_x, mouse_y)  # finds all the actual surrounding cells
            label = 0
            for neighbour in neighbours:
                if neighbour in self.mine_locations:
                    label += 1
            self.map[mouse_y][mouse_x] = f'images/{label}.png'
            if label == 0:
                for neighbour in neighbours:
                    self.handle_click(neighbour[0], neighbour[1])
                # TO-DO: POISTA? self.handle_adjacent_zeros(mouse_x, mouse_y, neighbours)        # So, this clicked cell was '0', therefore  in case an adjacent zero is found, all the zeros next to it should also be opened, and all the cells next to all the zeros as well!

    def surrounding_cells_coordinates(self, x, y):
        candidates = [(w,h) for h in range(y-1, y+1+1) for w in range(x-1,x+1+1) if 0<=w<self.width and 0<=h<self.height]
        candidates.remove((x,y))
        return candidates
        # print('\nsourrounding_cells_coordinates():', candidates)

    def draw_display(self):                     # for the matrix, draw the correct image for each cell
        self.screen.fill((0,0,0))
        for x in range (self.width):
            for y in range(self.height):
                cell_status = self.map[y][x]    # self.map is a list of lists; indices start from 0
                self.screen.blit(source=self.images[cell_status], dest=(x*self.scale, y*self.scale))

        pygame.display.flip()   # display.flip() will update the contents of the entire display. display.update() enables updating of just a part IF you specify which part
        self.clock.tick(30)
    
    def loop(self):
        while True:
            for event in pygame.event.get():
                self.inspect_event(event)
            self.draw_display()                                 # (2) then draw the screen after handling them

if __name__ == '__main__':
    beginner = 9,9,10
    intermediate = 16,16,40
    expert = 30,16,99           # width, height, mines
    Minesweeper(3,3,1)