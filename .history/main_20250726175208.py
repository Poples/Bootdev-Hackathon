# Example file showing a circle moving on screen
import pygame, sys, random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0


TILE_MAP_SIZE = 20
tile_map = [[random.randint(0, 2) for _ in range(TILE_MAP_SIZE)] for _ in range(TILE_MAP_SIZE)] 
TILE_SIZE = 64
tile_colors = {
    0: (34, 139, 34),   # grass
    1: (139, 69, 19),   # dirt
    2: (0, 255, 255)    # upgrade station (cyan)
}

MAP_PIXEL_WIDTH = TILE_MAP_SIZE * TILE_SIZE
MAP_PIXEL_HEIGHT = TILE_MAP_SIZE * TILE_SIZE

# Offset to draw the tile map centered on screen
map_offset_x = (screen.get_width() - MAP_PIXEL_WIDTH) // 2
map_offset_y = (screen.get_height() - MAP_PIXEL_HEIGHT) // 2

def draw_tile_map(screen, tile_map, offset_x, offset_y):
    for row_index, row in enumerate(tile_map):
        for col_index, tile in enumerate(row):
            tile_color = tile_colors.get(tile, (0, 0, 0))
            tile_rect = pygame.Rect(
                offset_x + col_index * TILE_SIZE,
                offset_y + row_index * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, tile_color, tile_rect)

def get_tile_coordinates_from_position(pos, offset_x, offset_y):
    tile_x = int((pos[0] - offset_x) // TILE_SIZE)
    tile_y = int((pos[1] - offset_y) // TILE_SIZE)
    return tile_x, tile_y

class Unit:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.pos = [pos_x, pos_y]



class Player(Unit):
    def __init__(self, name, health, width, height, move_speed, pos_x, pos_y, atk_speed):
        super().__init__(name, pos_x, pos_y)
        self.health = health
        self.width = width
        self. height = height
        self.speed = move_speed
        self.atk_speed = atk_speed
        self.__hit_box = [
            self.pos[0] - (self.width * .5), 
            self.pos[1] - (self.height * .5), 
            self.pos[0] + (self.width * .5),
            self.pos[1] + (self.height * .5)
        ] # to be determined later

    #player movement methods
    def move_left(self):
        self.pos[0] -= self.speed * dt

    def move_right(self):
        self.pos[0]  += self.speed * dt

    def move_up(self):
        self.pos[1] -= self.speed * dt

    def move_down(self):
        self.pos[1] += self.speed * dt





class Zombie(Unit):
    def __init__(self, width, height, speed):
        super().__init__(width, height, speed)





player_start_pos = [screen.get_width() / 2, screen.get_height() / 2]
player_speed = 100
player = Player("Jared", 100, 2, 2, player_speed, player_start_pos[0], player_start_pos[1], 1)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    draw_tile_map(screen, tile_map, map_offset_x, map_offset_y)

    tile_x, tile_y = get_tile_coordinates_from_position(player.pos, map_offset_x, map_offset_y)

    # Bounds check to avoid crashing
    if 0 <= tile_x < TILE_MAP_SIZE and 0 <= tile_y < TILE_MAP_SIZE:
        current_tile = tile_map[tile_y][tile_x]
        
        if current_tile == 2:  # example: tile type 1 = upgrade station
            print("Player is on an upgrade station!")
    # using asset as player image
    player_img =  pygame.image.load("assets/PlayerSprite.png")
    screen.blit(player_img, player.pos)

    # Player movements
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player.move_left()
    if keys[pygame.K_d]:
        player.move_right()
    if keys[pygame.K_s]:
        player.move_down()
    if keys[pygame.K_w]:
        player.move_up()



    

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
	