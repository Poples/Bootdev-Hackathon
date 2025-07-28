# main.py - Main game loop and initialization
import pygame
import sys
import random
import math

import MapGeneration as MG, PowerUpgrades
from PlayerInventory import PlayerInventory, XPOrb
from Units import Player, Zombie
from Combat import (shoot_at_nearest_zombie, update_bullets, check_bullet_zombie_collisions, 
                   continuous_spawn_system)
from GameUI import draw_game_ui, draw_game_over_screen, handle_player_input
from Camera import update_camera, get_map_offset , get_screen_position
from GameRenderer import render_game_objects

# =======================
# Constants
# =======================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

PLAYER_SPEED = 5
PLAYER_HEALTH = 100
PLAYER_ATK_SPEED = 1
PLAYER_PICKUP_RADIUS = 5

SHOT_COOLDOWN = 2000 # 2 seconds in milliseconds
BASE_SPAWN_INTERVAL = 3000  # 3 seconds initially in milliseconds
SPAWN_RATE_INCREASE = 0.95  # Multiply spawn interval by this each time (makes spawning faster)
DIFFICULTY_INCREASE_INTERVAL = 15000  # Increase difficulty every 15 seconds

#todo: sound, start screen, pause screen, game over screen, orbs getting sucked to player for visual clarity kappa
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Survival Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36,)
    # Load sprites
    sprites = {
        "player": pygame.image.load("assets/PlayerSprite.png"),
        "walker_zombie": pygame.image.load("assets/WalkerZombieSprite.png"),
        "tank_zombie": pygame.image.load("assets/TankZombieSprite.png"),
        "bullet_img": pygame.image.load("assets/BulletSprite.png"),
    }   
    # Game world setup
    tile_map = MG.generate_tile_map()
    MAP_PIXEL_WIDTH = MG.TILE_MAP_SIZE * MG.TILE_SIZE
    MAP_PIXEL_HEIGHT = MG.TILE_MAP_SIZE * MG.TILE_SIZE
    # Game object lists
    
    zombies = []
    bullets = []
    xp_orbs = []
    health_orbs = []
    current_buffs = []

    has_picked_up = set() # Set to track which upgrade tiles have been picked up

    # Game configuration constants
    #screen_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height()) #getting screen as rectangle for clamp
    # Camera variables
    camera_x = 0
    camera_y = 0
    # Offset to draw the tile map centered on screen
    map_offset_x = (screen.get_width() - MAP_PIXEL_WIDTH) // 2
    map_offset_y = (screen.get_height() - MAP_PIXEL_HEIGHT) // 2
    # Initialize player in the center of the screen
    player_start_pos = [screen.get_width() / 2, screen.get_height() / 2]
    player = Player("Jared", PLAYER_HEALTH, PLAYER_SPEED, PLAYER_ATK_SPEED, sprites["player"], player_start_pos)
    
    player_inventory = PlayerInventory()
    player.inventory = player_inventory 
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
        zombies.append(Zombie(f"Zombie_{i}", zombie_x, zombie_y,"WalkerZombie"))

    last_shot_time = 0
    last_spawn_time = 0
    game_start_time = 0
    running = True
    DELTA_TIME = 0
    game_start_time = pygame.time.get_ticks()

    # Main game loop
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Clear screen
        screen.fill("black")
        # Get current time
        current_time = pygame.time.get_ticks()
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
                    has_picked_up.add(tile_key)
                    # Draw everything before pausing
                    render_game_objects(screen, player, zombies, bullets, sprites, camera_x, camera_y)

                    draw_game_ui(screen, font, player, zombies, bullets, current_time, last_shot_time, SHOT_COOLDOWN,
                                game_start_time, DIFFICULTY_INCREASE_INTERVAL, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE,
                                last_spawn_time)
                    player_inventory.draw_inventory(screen, font)

                    for orb in xp_orbs[:]:
                        XPOrb.draw(orb, screen, camera_x, camera_y)

                    pause_start_time = pygame.time.get_ticks()
                    pygame.display.flip()  # Show the last game frame
                    if random.randint(1, 2) == 1:
                        PowerUpgrades.add_buff(current_buffs, "Speed Boost", 10)
                        player.speed = player.speed + 2
                        # Pause and show the random buff screen
                        PowerUpgrades.open_randombuff_screen(screen, font, screen.get_width(), screen.get_height(), " Extra Speed", 10)
                    else:
                        PowerUpgrades.add_buff(current_buffs, "Pickup Radius", 10)
                        player.pickup_radius = player.pickup_radius + 5
                        for orb in xp_orbs:
                            orb.pickup_radius = player.pickup_radius
                        # Pause and show the random buff screen
                        PowerUpgrades.open_randombuff_screen(screen, font, screen.get_width(), screen.get_height(), "Pickup Radius", 10)
                    clock.tick()  # Reset clock after pause
                    DELTA_TIME = 0
                    # After choosing upgrade, replace the tile
                    tile_map[tile_y][tile_x] = random.choice([0, 1])
                    
                    pause_duration = pygame.time.get_ticks() - pause_start_time
                    game_start_time = game_start_time + pause_duration
                    continue  # Skip the rest of the update this frame
        # reduce buff durations:
        current_buffs, buffs_to_remove = PowerUpgrades.update_buffs(current_buffs, DELTA_TIME)
        for buff_name in buffs_to_remove:
            if buff_name == "Speed Boost":
                player.speed = player.speed - 2
            elif buff_name == "Pickup Radius":
                player.pickup_radius = player.pickup_radius - 5
                for orb in xp_orbs:
                    orb.pickup_radius = player.pickup_radius
        
        PowerUpgrades.draw_buffs(screen, font, screen.get_width(), screen.get_height() , current_buffs)
        # Draw inventory
        player_inventory.draw_inventory(screen, font)
        # Draw XP orbs
        for orb in xp_orbs[:]:
            if orb.check_collision_with_player(player):
                orb.collected = True
                xp_orbs.remove(orb)
                player_inventory.add_item("XP", orb.value)

                if (player_inventory.get_quantity("XP") >= 10 and player_inventory.level < 10):
                    player_inventory.level = player_inventory.level + 1
                    player_inventory.remove_item("XP", 10)
                    #logic for leveling up here
                    pause_start_time = pygame.time.get_ticks()
                    pygame.display.flip()  # Show the last game frame
                    PowerUpgrades.open_levelup_screen(screen, player, PowerUpgrades.apply_upgrade, font, screen.get_width(), screen.get_height())
                    clock.tick()  # Reset clock after pause
                    DELTA_TIME = 0
                    tile_map[tile_y][tile_x] = random.choice([0, 1])
                    pause_duration = pygame.time.get_ticks() - pause_start_time
                    game_start_time = game_start_time + pause_duration
                    continue  # Skip the rest of the update this frame
            else:
                XPOrb.draw(orb, screen, camera_x, camera_y)\
        # Draw health orbs
        for orb in health_orbs[:]:
            if orb.check_collision_with_player(player):
                orb.collected = True
                health_orbs.remove(orb)
                player.gain_health(orb.value)
            else:
                orb.draw(screen, camera_x, camera_y)

        # Combat system
        shot_fired, last_shot_time = shoot_at_nearest_zombie(player, zombies, bullets, current_time, 
                                                            last_shot_time, SHOT_COOLDOWN)
        update_bullets(bullets, DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        check_bullet_zombie_collisions(player, bullets, zombies,xp_orbs,health_orbs)
        # Spawning system
        last_spawn_time = continuous_spawn_system(player.pos, zombies, current_time, last_spawn_time, 
                                                game_start_time, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE, 
                                                DIFFICULTY_INCREASE_INTERVAL, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT,player_inventory)
        # Update zombies
        for zombie in zombies:
            zombie.move_towards_player(player.pos, DELTA_TIME)
            if zombie.check_collision_with_player(player):
                zombie.attack_player(player, current_time)
        # Render all game objects
        render_game_objects(screen, player, zombies, bullets, sprites, camera_x, camera_y)
        # Draw UI
        draw_game_ui(screen, font, player, zombies, bullets, current_time, last_shot_time, SHOT_COOLDOWN,
                    game_start_time, DIFFICULTY_INCREASE_INTERVAL, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE,
                    last_spawn_time)
        
        # Handle game over
        is_game_over = draw_game_over_screen(screen, font, player)
        # Player movements
        keys = pygame.key.get_pressed()
        # Handle input
        should_quit = handle_player_input(keys, player, DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, is_game_over)

        if should_quit:
            running = False
        # Update display
        pygame.display.flip()

        DELTA_TIME = clock.tick(FPS) / 1000
    pygame.quit()

if __name__ == "__main__":
    main()
