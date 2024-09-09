import pygame
from random import sample

# cell = a square of the map

class Minesweeper:
    def __init__(self, width, height, mines):
        pygame.init()
        self.mouse_pos = (0,0)

        self.scale = 50        # how many px in height and width should each cell (image) be?
        self.height = height    # map height measured in in rows
        self.width = width
        
        self.mines = mines
        if mines > width*height:
            return f'too many mines, max is {width*height} for this size'
        
        self.images = {}        # {name : loaded image}
        self.load_images()
        
        self.screen = pygame.display.set_mode((self.scale*height, self.scale*width)) # each .png is 100 px, which is large.
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
        self.started = False                                                            # the mines will be placed AFTER the first click, as in real minesweeper. Otherwise you could lose on the first click. For that, we need to keep track on if the first click has already commenced or not.
        self.map = [['images/unclicked.png' for x in range(1, self.width+1)] for y in range(1, self.height+1)]   # the visuals; names of the images!

    def inspect_event(self, event):
        #self.mouse_tracker()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()                               # to-do: make a check if it's on a cell, if needed!
            print(f'mouse_x//scale, mouse_y//scale: {mouse_x//self.scale, mouse_y//self.scale}')  # if each cell width is e.g. 100 px, then if you click e.g. on x-coord 540, it's the 6th column (40 would be 1st)
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
            print('x//self.scale, y//self.scale:', x//self.scale, y//self.scale)
            self.mouse_pos = mouse_pos

    def handle_first_click(self, mouse_x, mouse_y):
        print("\nhandle_first_click")
        self.started = True

        # based on which cell was clicked, place the mines (do not place a mine in the cell that was just clicked)
        self.available_coordinates = [(x,y) for y in range(1, self.height+1) for x in range(1, self.width+1) if (x,y) != (mouse_x, mouse_y)]
        self.mine_locations = set(sample(self.available_coordinates,self.mines))
        print('klikattiin koordinaatteja', mouse_x, mouse_y, 'ja miinat laitettiin seuraavasti:\n', self.mine_locations)
    
    def handle_click(self, mouse_x, mouse_y):
        print('\nhandle_click')
        print('mouse_x, mouse_y:', (mouse_x, mouse_y))  # HUOM! (15,0) on x-painike c:

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
    Minesweeper(expert[0], expert[1], expert[2])