# Example file showing a circle moving on screen
import pygame, sys

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

class Unit:
    def __init__(self, width, height, speed):
        self.width = width
        self.height = height
        self.speed = speed



class Player(Unit):
    def __init__(self, width, height, speed):
        super().__init__(width, height, speed)


class Zombie(Unit):
    def __init__(self, width, height, speed):
        super().__init__(width, height, speed)





player_pos = [screen.get_width() / 2, screen.get_height() / 2]
player_speed = 100

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    pygame.draw.circle(screen, "green", player_pos, 20)

    # Player movements
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_pos[0] -= player_speed * dt
    if keys[pygame.K_d]:
        player_pos[0] += player_speed * dt
    if keys[pygame.K_s]:
        player_pos[1] += player_speed * dt
    if keys[pygame.K_w]:
        player_pos[1]-= player_speed * dt



    

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
	