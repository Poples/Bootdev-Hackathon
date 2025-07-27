# main.py - Main game loop and initialization
import pygame
import sys
import random
import math
import MapGeneration as MG
from PlayerInventory import PlayerInventory
from Units import Player, Zombie
from Combat import (shoot_at_nearest_zombie, update_bullets, check_bullet_zombie_collisions, 
                   continuous_spawn_system)
from GameUI import draw_game_ui, draw_game_over_screen, handle_player_input
from Camera import update_camera, get_map_offset
from GameRenderer import render_game_objects

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

font = pygame.font.SysFont(None, 36,)

# Game world setup
tile_map = MG.generate_tile_map()
MAP_PIXEL_WIDTH = MG.TILE_MAP_SIZE * MG.TILE_SIZE
MAP_PIXEL_HEIGHT = MG.TILE_MAP_SIZE * MG.TILE_SIZE
# Camera variables
camera_x = 0
camera_y = 0

# Game configuration constants
PLAYER_SPEED = 200
PLAYER_HEALTH = 100
PLAYER_ATK_SPEED = 1
SHOT_COOLDOWN = 2000  # 2 seconds in milliseconds
BASE_SPAWN_INTERVAL = 3000  # 3 seconds initially in milliseconds
SPAWN_RATE_INCREASE = 0.95  # Multiply spawn interval by this each time (makes spawning faster)
DIFFICULTY_INCREASE_INTERVAL = 15000  # Increase difficulty every 15 seconds

# Load sprites
player_img = pygame.image.load("assets/PlayerSprite.png")
zombie_img = pygame.image.load("assets/WalkerZombieSprite.png")
bullet_img = pygame.image.load("assets/BulletSprite.png")

# Initialize player
player_start_pos = [screen.get_width() / 2, screen.get_height() / 2]
player = Player("Jared", PLAYER_HEALTH, PLAYER_SPEED, player_start_pos[0], player_start_pos[1], PLAYER_ATK_SPEED, player_img)

# Game object lists
zombies = []
bullets = []

# Game state variables
last_shot_time = 0
last_spawn_time = 0
game_start_time = 0


# Offset to draw the tile map centered on screen
map_offset_x = (screen.get_width() - MAP_PIXEL_WIDTH) // 2
map_offset_y = (screen.get_height() - MAP_PIXEL_HEIGHT) // 2

# Player inventory and tile tracking
player_inventory = PlayerInventory()
has_picked_up = set()  # track which tiles we've already picked up

# Spawn initial zombies around the map
for i in range(5):  # Start with 5 zombies
    # Spawn zombies in a circle around the player at a safe distance
    angle = (i / 5) * 2 * math.pi
    spawn_distance = 300  # pixels away from player
    zombie_x = player.pos[0] + math.cos(angle) * spawn_distance
    zombie_y = player.pos[1] + math.sin(angle) * spawn_distance
    
    # Ensure zombies spawn within map bounds
    zombie_x = max(50, min(MAP_PIXEL_WIDTH - 50, zombie_x))
    zombie_y = max(50, min(MAP_PIXEL_HEIGHT - 50, zombie_y))
    
    zombie = Zombie(f"Zombie_{i}", zombie_x, zombie_y)
    zombies.append(zombie)

# Initialize game start time
game_start_time = pygame.time.get_ticks()

# Main game loop

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear screen
    screen.fill("black")
    
    # Update camera
    camera_x, camera_y = update_camera(player.pos, screen.get_width(), screen.get_height())
    map_offset_x, map_offset_y = get_map_offset(camera_x, camera_y)
    
    # Draw tile map
    MG.draw_tile_map(screen, tile_map, map_offset_x, map_offset_y)

    # Handle tile pickup logic
    tile_x = int(player.pos[0] // MG.TILE_SIZE)
    tile_y = int(player.pos[1] // MG.TILE_SIZE)
    
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
    #screen.blit(PLAYER.image, PLAYER.pos)

    # Get current time
    current_time = pygame.time.get_ticks()
    
    # Combat system
    shot_fired, last_shot_time = shoot_at_nearest_zombie(player.pos, zombies, bullets, current_time, 
                                                        last_shot_time, SHOT_COOLDOWN)
    update_bullets(bullets, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
    check_bullet_zombie_collisions(bullets, zombies)
    
    # Spawning system
    last_spawn_time = continuous_spawn_system(player.pos, zombies, current_time, last_spawn_time, 
                                            game_start_time, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE, 
                                            DIFFICULTY_INCREASE_INTERVAL, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
    
    # Update zombies
    for zombie in zombies:
        zombie.move_towards_player(player.pos, dt)
        if zombie.check_collision_with_player(player):
            zombie.attack_player(player, current_time)
    
    # Render all game objects
    render_game_objects(screen, player, zombies, bullets, zombie_img, bullet_img, camera_x, camera_y)
    
    # Draw UI
    draw_game_ui(screen, font, player, zombies, bullets, current_time, last_shot_time, SHOT_COOLDOWN,
                game_start_time, DIFFICULTY_INCREASE_INTERVAL, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE,
                last_spawn_time)
    
    # Draw inventory
    player_inventory.draw_inventory(screen, font)
    
    # Handle game over
    is_game_over = draw_game_over_screen(screen, font, player)
  
    # Player movements
    keys = pygame.key.get_pressed()

    # Handle input
    should_quit = handle_player_input(keys, player, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, is_game_over)

    if should_quit:
        running = False


    # Update display
    pygame.display.flip()

    dt = clock.tick(60) / 1000

pygame.quit()
	
