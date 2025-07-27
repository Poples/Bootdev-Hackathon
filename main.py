# Example file showing a circle moving on screen
import pygame, sys

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

class Unit:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.pos = [pos_x, pos_y]


class Player(Unit):
    def __init__(self, name):
        PLAYER_START_POS = [screen.get_width() / 2, screen.get_height() / 2] # Center of screen
        self.image = pygame.image.load("assets/PlayerSprite.png")
        IMG_rect = self.image.get_rect(center=PLAYER_START_POS) # Centralize the image on the center on the screen
        hit_box_rect = self.image.get_rect(topleft=self.pos) # Setting the start point for hit box
        super().__init__(name, IMG_rect[0], IMG_rect[1])
        self.health = 100
        self.width, self.height = self.image.get_size()
        self.speed = 100
        self.atk_speed = 1
        
    # Player movement methods
    def move_left(self):
        self.pos[0] -= self.speed * dt

    def move_right(self):
        self.pos[0]  += self.speed * dt

    def move_up(self):
        self.pos[1] -= self.speed * dt

    def move_down(self):
        self.pos[1] += self.speed * dt

    


class Zombie(Unit):
    def __init__(self, name, pos_x, pos_y, width, height, move_speed):
        super().__init__(name, pos_x, pos_y)
        self.width = width
        self.height = height
        self.move_speed = move_speed


PLAYER_START_POS = [screen.get_width() / 2, screen.get_height() / 2]
PLAYER = Player("Jared")


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # using asset as player image
    screen.blit(PLAYER.image, PLAYER.pos)
  
    # Player movements
    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        PLAYER.move_left()

    if keys[pygame.K_d]:
        PLAYER.move_right()

    if keys[pygame.K_s]:
        PLAYER.move_down()

    if keys[pygame.K_w]:
        PLAYER.move_up()

    



    

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
	