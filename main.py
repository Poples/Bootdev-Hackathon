# main.py - Main game loop and initialization
from logging import info
import pygame
import sys
import random
import math

from GameState import GameState
import GameLogic
from GameUI import GameUI

import MapGeneration as MG, PowerUpgrades
from PlayerInventory import PlayerInventory, XPOrb
from Units import Player, Zombie, RangedZombie
from Combat import (shoot_at_nearest_zombie, update_bullets, check_bullet_zombie_collisions, 
                   continuous_spawn_system)
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

#todo: add upper bounds for health, remove prints, more sounds?(zombie death), start screen, game over screen(stats like kills and time),
#  orbs getting sucked to player for visual clarity kappa
#combat file needs to merge with Gamelogic 
# logic in units.py need to go to gamelogic
#logic in combat needs to go to gamerenderer
#spawn and other logic from main needs to go to gamelogic
# rendering logic in main needs to go to gamerenderer
def main():
    # Initialization 
    pygame.init()
    pygame.mixer.init() #sounds
    pygame.display.set_caption("Zombie Survival Game")
    clock = pygame.time.Clock()

    game_ui = GameUI(pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h)),
                     pygame.font.SysFont(None, 36))


    MAP_PIXEL_WIDTH = MG.TILE_MAP_SIZE * MG.TILE_SIZE
    MAP_PIXEL_HEIGHT = MG.TILE_MAP_SIZE * MG.TILE_SIZE
    player_start_pos = [game_ui.screen.get_width() / 2, game_ui.screen.get_height() / 2]

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

    gs.player = Player("Jared", PLAYER_HEALTH,PLAYER_MAX_HEALTH, PLAYER_SPEED, PLAYER_ATK_SPEED, sprites["player"], player_start_pos, game_ui)

    gs.player.player_inventory = PlayerInventory()

    gs.tile_map = MG.generate_tile_map()

    gs.game_start_time = pygame.time.get_ticks()

    GameLogic.initial_zomebie_spawn(gs, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
    
    DELTA_TIME = 0
    # Main game loop
    while gs.running:
        game_ui.screen.fill("black") #clear last frame with black background

        
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
            camera_x, camera_y = update_camera(gs.player.pos, game_ui.screen.get_width(), game_ui.screen.get_height())
            map_offset_x, map_offset_y = get_map_offset(camera_x, camera_y)
            MG.draw_tile_map(game_ui.screen, gs.tile_map, map_offset_x, map_offset_y)
            render_game_objects(game_ui.screen, gs.player, gs.zombies, gs.bullets, sprites, camera_x, camera_y)
            menu_choice = game_ui.draw_pause_menu(game_ui.screen, game_ui.font)

            if menu_choice == "resume":
                gs.pause_duration = pygame.time.get_ticks() - gs.pause_start_time
                gs.game_start_time += gs.pause_duration
                gs.paused = False
            elif menu_choice == "quit":
                gs.running = False

            pygame.display.flip()  # Update the display
            clock.tick(FPS)  # Maintain frame rate
            continue  # Skip the rest of the loop if paused
        # Player movements
        if not gs.paused:
            is_game_over = game_ui.draw_game_over_screen(game_ui.screen, game_ui.font, gs.player)
            keys = pygame.key.get_pressed()
            # Handle input
            should_quit = game_ui.handle_player_input(keys, gs.player, DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, is_game_over)

            if should_quit:
                gs.running = False

        
        # Time and camera updates
        current_time = pygame.time.get_ticks()
        camera_x, camera_y = update_camera(gs.player.pos, game_ui.screen.get_width(), game_ui.screen.get_height())
        map_offset_x, map_offset_y = get_map_offset(camera_x, camera_y)

        # Draw tile map
        MG.draw_tile_map(game_ui.screen, gs.tile_map, map_offset_x, map_offset_y)
        
        # Game Updates
        GameLogic.on_shrine_check(gs, MG, sounds, game_ui.screen, game_ui.font, clock)
        GameLogic.update_buffs(gs, DELTA_TIME)
        
        PowerUpgrades.draw_buffs(game_ui.screen, game_ui.font, game_ui.screen.get_width(), game_ui.screen.get_height() , gs.current_buffs)
        # Draw inventory
        gs.player.player_inventory.draw_inventory(game_ui.screen, game_ui.font)
        # Draw XP orbs
        GameLogic.handle_xp_orbs(gs, MG,game_ui.screen, camera_x, camera_y, game_ui.font, clock, sounds)
        # Draw health orbs
        GameLogic.handle_health_orbs(gs, game_ui.screen, camera_x, camera_y)



        # --- TO GAMELOGIC ---
        # Combat system
        shot_fired, gs.last_shot_time = shoot_at_nearest_zombie(gs, current_time, SHOT_COOLDOWN)
        sounds["Shoot"].play() if shot_fired else None

        # Spawning system
        gs.last_spawn_time = continuous_spawn_system(gs, current_time, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE, 
                                                DIFFICULTY_INCREASE_INTERVAL, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        
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
                
        # --- end of TO GAMELOGIC ---


        # --- to GameRenderer ---
        update_bullets(gs.bullets, DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        check_bullet_zombie_collisions(gs)

        # Render all game objects
        render_game_objects(game_ui.screen, gs.player, gs.zombies,gs.bullets, sprites, camera_x, camera_y)

        # Draw zombie projectiles
        for projectile in gs.zombie_projectiles:
            projectile.draw(game_ui.screen, camera_x, camera_y, sprites["zombie_spit"])

        # --- end of to GameRenderer ---

        # --- to GameUI ---
        # Draw UI
        game_ui.draw_damage_flash()
        game_ui.draw_status_bars(gs.player)
        game_ui.draw_game_ui(game_ui.screen, game_ui.font, gs,
                     SHOT_COOLDOWN, current_time, DIFFICULTY_INCREASE_INTERVAL, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE)
        # --- end of to GameUI ---
        
        pygame.display.flip()
        DELTA_TIME = clock.tick(FPS) / 1000
    pygame.quit()

if __name__ == "__main__":
    main()
