# Example file showing a circle moving on screen
import pygame, sys, random, MapGeneration as MG
from PlayerInventory import PlayerInventory

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.SysFont(None, 36,)

tile_map = MG.generate_tile_map()
MAP_PIXEL_WIDTH = MG.TILE_MAP_SIZE * MG.TILE_SIZE
MAP_PIXEL_HEIGHT = MG.TILE_MAP_SIZE * MG.TILE_SIZE
# Offset to draw the tile map centered on screen
map_offset_x = (screen.get_width() - MAP_PIXEL_WIDTH) // 2
map_offset_y = (screen.get_height() - MAP_PIXEL_HEIGHT) // 2

class Unit:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.pos = [pos_x, pos_y]

class Player(Unit):
    def __init__(self, name, health, width, height, move_speed, pos_x, pos_y, atk_speed):
        super().__init__(name, pos_x, pos_y)
        self.health = health
        self.width = width
        self.height = height
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
player_speed = 200
player = Player("Jared", 100, 2, 2, player_speed, player_start_pos[0], player_start_pos[1], 1)


player_inventory = PlayerInventory()
has_picked_up = set()  # track which tiles we've already picked up

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")
    MG.draw_tile_map(screen, tile_map, map_offset_x, map_offset_y)

    tile_x, tile_y = MG.get_tile_coordinates_from_position(player.pos, map_offset_x, map_offset_y)
    if 0 <= tile_x < MG.TILE_MAP_SIZE and 0 <= tile_y < MG.TILE_MAP_SIZE:
        current_tile = tile_map[tile_y][tile_x]
        if current_tile == 2:
            tile_key = (tile_x, tile_y)
            if tile_key not in has_picked_up:
                # Give the player one random upgrade
                player_inventory.add_item("Upgrade Station Token", 1)
                # Mark tile so we don't pick up twice
                has_picked_up.add(tile_key)
                # Change the tile to grass (0) or dirt (1)
                tile_map[tile_y][tile_x] = random.choice([0, 1])
            #text_surface = font.render("IN UPGRADE STATION", True, (255, 255, 0))  # yellow
            #text_rect = text_surface.get_rect(topright=(screen.get_width() - 10, 10))  # 10px padding from top-right corner
            #screen.blit(text_surface, text_rect)
    # using asset as player image
    player_img =  pygame.image.load("assets/PlayerSprite.png")
    screen.blit(player_img, player.pos)

    player_inventory.draw_inventory(screen,font)

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

    #enemy
    # WalkerZombie = pygame.image.load("assets/WalkerZombieSprite.png")
    # screen.blit(WalkerZombie, (500, 600))



    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
	