# main.py - Main game loop and initialization
from logging import info
import pygame
import sys
import random
import math

from GameState import GameState
import GameLogic as GameLogic

import MapGeneration as MG, PowerUpgrades
from PlayerInventory import PlayerInventory, XPOrb
from Units import Player, Zombie, RangedZombie
from Combat import (shoot_at_nearest_zombie, update_bullets, check_bullet_zombie_collisions, 
                   continuous_spawn_system)
from GameUI import draw_game_ui, draw_game_over_screen, handle_player_input, draw_pause_menu, draw_status_bars
from Camera import update_camera, get_map_offset , get_screen_position
from GameRenderer import render_game_objects

# =======================
# Constants
# =======================
FPS = 60
PLAYER_SPEED = 5
PLAYER_HEALTH = 100
PLAYER_MAX_HEALTH = 100
PLAYER_ATK_SPEED = 1
PLAYER_PICKUP_RADIUS = 5
SHOT_COOLDOWN = 2000 # 2 seconds in milliseconds
BASE_SPAWN_INTERVAL = 3000  # 3 seconds initially in milliseconds
SPAWN_RATE_INCREASE = 0.95  # Multiply spawn interval by this each time (makes spawning faster)
DIFFICULTY_INCREASE_INTERVAL = 15000  # Increase difficulty every 15 seconds

#todo: change zombie spawn based on difficulty not level, add upper bounds for health, remove prints, more sounds?(zombie death), start screen, pause screen, game over screen(stats like kills and time), orbs getting sucked to player for visual clarity kappa
def main():
    # Initialization 
    pygame.init()
    pygame.mixer.init() #sounds

    info = pygame.display.Info()
    SCREEN_WIDTH = info.current_w
    SCREEN_HEIGHT = info.current_h
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Survival Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36,)

    # Load assets
    sprites = {
        "player": pygame.transform.scale(pygame.image.load("assets/PlayerSprite.png"), (64, 64)),
        "walker_zombie": pygame.transform.scale(pygame.image.load("assets/WalkerZombieSprite.png"), (64, 64)),
        "tank_zombie": pygame.transform.scale(pygame.image.load("assets/TankZombieSprite.png"), (64, 64)),
        "bullet_img": pygame.transform.scale(pygame.image.load("assets/BulletSprite.png"), (48, 48)),
        "ranged_zombie": pygame.transform.scale(pygame.image.load("assets/RangedZombieSprite.png"), (64, 64)),
        "zombie_spit": pygame.transform.scale(pygame.image.load("assets/RangedZombieSpitSprite.png"), (64, 64)),
    }
    sounds = {
        "Shoot": pygame.mixer.Sound("assets/mixkit_Gunshot.mp3"),
        "Shrine": pygame.mixer.Sound("assets/mixkit_Shrine.wav"),
        "Levelup": pygame.mixer.Sound("assets/mixkit_Levelup.wav"),
        "OrbPickup": pygame.mixer.Sound("assets/mixkit_OrbPickup.wav")
    }

    # Game State Setup
    gs = GameState()
    gs.tile_map = MG.generate_tile_map()
    # Game world setup
    MAP_PIXEL_WIDTH = MG.TILE_MAP_SIZE * MG.TILE_SIZE
    MAP_PIXEL_HEIGHT = MG.TILE_MAP_SIZE * MG.TILE_SIZE
    player_start_pos = [screen.get_width() / 2, screen.get_height() / 2]

    gs.player = Player("Jared", PLAYER_HEALTH,PLAYER_MAX_HEALTH, PLAYER_SPEED, PLAYER_ATK_SPEED, sprites["player"], player_start_pos)

    gs.player.player_inventory = PlayerInventory()

    GameLogic.initial_zomebie_spawn(gs, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
    
    gs.game_start_time = pygame.time.get_ticks()


    DELTA_TIME = 0
    # Main game loop
    while gs.running:
        screen.fill("black") #clear last frame with black background
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gs.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and gs.player.health > 0:
            # Only allow pausing if player is alive
                if not gs.paused:
                    gs.paused = True
                    gs.pause_start_time = pygame.time.get_ticks()
                else:
                    gs.pause_duration = pygame.time.get_ticks() - gs.pause_start_time
                    gs.game_start_time += gs.pause_duration
                    gs.paused = False
        #pause menu
        if gs.paused:
            camera_x, camera_y = update_camera(gs.player.pos, screen.get_width(), screen.get_height())
            map_offset_x, map_offset_y = get_map_offset(camera_x, camera_y)
            MG.draw_tile_map(screen, gs.tile_map, map_offset_x, map_offset_y)
            render_game_objects(screen, gs.player, gs.zombies, gs.bullets, sprites, camera_x, camera_y)
            menu_choice = draw_pause_menu(screen, font)

            if menu_choice == "resume":
                gs.pause_duration = pygame.time.get_ticks() - gs.pause_start_time
                gs.game_start_time += gs.pause_duration
                gs.paused = False
            elif menu_choice == "quit":
                gs.running = False

            pygame.display.flip()  # Update the display
            clock.tick(FPS)  # Maintain frame rate
            continue  # Skip the rest of the loop if paused

        # Time and camera updates
        current_time = pygame.time.get_ticks()
        camera_x, camera_y = update_camera(gs.player.pos, screen.get_width(), screen.get_height())
        map_offset_x, map_offset_y = get_map_offset(camera_x, camera_y)
        

        # Draw tile map
        MG.draw_tile_map(screen, gs.tile_map, map_offset_x, map_offset_y)
        
        # Game Updates
        GameLogic.on_shrine_check(gs.player, MG, sounds, gs.tile_map, gs.xp_orbs, gs.player_inventory, gs.current_buffs, screen, font, clock, gs.game_start_time)
        GameLogic.update_buffs(gs, DELTA_TIME)
        
        PowerUpgrades.draw_buffs(screen, font, screen.get_width(), screen.get_height() , gs.current_buffs)
        # Draw inventory
        gs.player.player_inventory.draw_inventory(screen, font)
        # Draw XP orbs
        GameLogic.handle_xp_orbs(gs,MG, screen, camera_x, camera_y, font, clock, sounds)
        # Draw health orbs
        GameLogic.handle_health_orbs(gs, screen, camera_x, camera_y)



        # Combat system
        shot_fired, gs.last_shot_time = shoot_at_nearest_zombie(gs.player, gs.zombies, gs.bullets, current_time, 
                                                            gs.last_shot_time, SHOT_COOLDOWN)
        sounds["Shoot"].play() if shot_fired else None

        update_bullets(gs.bullets, DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        check_bullet_zombie_collisions(gs.player, gs.bullets, gs.zombies,gs.xp_orbs,gs.health_orbs)
        # Spawning system
        gs.last_spawn_time = continuous_spawn_system(gs.player.pos, gs.zombies, current_time, gs.last_spawn_time, 
                                                gs.game_start_time, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE, 
                                                DIFFICULTY_INCREASE_INTERVAL, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT,gs.player_inventory)
        # Update zombies
        for zombie in gs.zombies:
            zombie.move_towards_player(gs.player.pos, DELTA_TIME)
            if zombie.check_collision_with_player(gs.player):
                zombie.attack_player(gs.player, current_time)
            
            # Check if this is a ranged zombie and if it can shoot
            if hasattr(zombie, 'shoot_at_player'):  # Check if it's a RangedZombie
                projectile = zombie.shoot_at_player(gs.player.pos, current_time)
                if projectile:
                    projectile.creation_time = current_time
                    gs.zombie_projectiles.append(projectile)
        
        # Update zombie projectiles
        for projectile in gs.zombie_projectiles[:]:
            projectile.update(DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, current_time)
            if not projectile.active:
                gs.zombie_projectiles.remove(projectile)
            elif projectile.check_collision_with_player(gs.player):
                gs.player.take_damage(projectile.damage)
                projectile.active = False
                gs.zombie_projectiles.remove(projectile)
        
        # Render all game objects
        render_game_objects(screen, gs.player, gs.zombies,gs.bullets, sprites, camera_x, camera_y)
        
        # Draw zombie projectiles
        for projectile in gs.zombie_projectiles:
            projectile.draw(screen, camera_x, camera_y, sprites["zombie_spit"])
        
        # Draw UI
        draw_status_bars(screen, font, gs.player, gs.player_inventory)
        draw_game_ui(screen, font, gs.player, gs.zombies, gs.bullets, current_time, gs.last_shot_time, SHOT_COOLDOWN,
                    gs.game_start_time, DIFFICULTY_INCREASE_INTERVAL, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE,
                    gs.last_spawn_time)
        
        # Handle game over
        
        # Player movements
        if not gs.paused:
            is_game_over = draw_game_over_screen(screen, font, gs.player)
            keys = pygame.key.get_pressed()
            # Handle input
            should_quit = handle_player_input(keys, gs.player, DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, is_game_over)

            if should_quit:
                gs.running = False
        # Update display
        pygame.display.flip()

        DELTA_TIME = clock.tick(FPS) / 1000
    pygame.quit()

if __name__ == "__main__":
    main()
