# Example file showing a circle moving on screen
import pygame, sys, random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0



tile_map = [[random.randint(0, 1) for _ in range(20)] for _ in range(12)]  # 20x12 tiles
TILE_SIZE = 64
tile_colors = {0: (34, 139, 34), 1: (139, 69, 19)}

def draw_tile_map(screen, tile_map):
    for row_index, row in enumerate(tile_map):
        for col_index, tile in enumerate(row):
            tile_color = tile_colors.get(tile, (0, 0, 0))
            tile_rect = pygame.Rect(col_index * TILE_SIZE, row_index * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, tile_color, tile_rect)



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
	