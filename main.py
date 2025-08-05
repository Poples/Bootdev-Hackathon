# main.py - Main game loop and initialization
from logging import info
import pygame

import GameRenderer as GameRenderer
from GameState import GameState
import GameLogic
from GameUI import GameUI
import PowerUpgrades
import config

import Combat
from PlayerInventory import PlayerInventory, XPOrb
from Units import Player, Zombie, RangedZombie
from Camera import update_camera, get_map_offset , get_screen_position

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
# playerinventory needs to be moved to gamelogic or units maybe
#camera needs to be moved to gamerenderer
#powerupgrades needs to be moved to gamelogic and gamerenderer
# units renamed to entities 
# logic in units.py need to go to gamelogic
# logic in combat needs to go to gamerenderer
# move most consants to config.py
# cleanup pause logic and move into game ui and gamestate
def main():
    # Initialization 
    pygame.init()
    pygame.mixer.init() #sounds
    pygame.display.set_caption("Zombie Survival Game")
    clock = pygame.time.Clock()
    game_ui = GameUI(pygame.display.set_mode((pygame.display.Info().current_w, pygame.display.Info().current_h)),
                     pygame.font.SysFont(None, 36))
    
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
    gs.tile_map = GameRenderer.generate_tile_map()
    gs.game_start_time = pygame.time.get_ticks()
    GameLogic.initial_zombie_spawn(gs)
    # Main game loop
    while gs.running:
        game_ui.screen.fill("black") #clear last frame with black background
        # Handle events

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gs.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and gs.player.health > 0:
                gs.toggle_pause()
        #pause menu
        if gs.paused:
            if not gs.game_over:
                game_ui.draw_pause_screen(gs, game_ui, sprites)
                clock.tick(FPS)  # Maintain frame rate
                continue  # Skip the rest of the loop if paused
            else:
                game_ui.draw_game_over_screen(gs, game_ui, sprites)
                if GameLogic.handle_player_input(pygame.key.get_pressed(), gs):
                    gs.running = False
                clock.tick(FPS)
                continue
        if gs.player.health <= 0:
            if not gs.game_over:
                gs.game_ended_time = pygame.time.get_ticks() - gs.game_start_time
                gs.game_over = True
            gs.toggle_pause()  # Pause the game if player is dead
            
        # Time and camera updates
        #current_time = pygame.time.get_ticks()

        camera_x, camera_y = update_camera(gs.player.pos, game_ui.screen.get_width(), game_ui.screen.get_height())
        map_offset_x, map_offset_y = get_map_offset(camera_x, camera_y)


        # --- to GameRenderer ---
        # Draw tile map
        GameRenderer.draw_tile_map(game_ui.screen, gs.tile_map, map_offset_x, map_offset_y)
        GameRenderer.update_bullets(gs.bullets, gs.delta_time)
        # Render all game objects
        GameRenderer.render_game_objects(game_ui.screen, gs.player, gs.zombies,gs.bullets, sprites, camera_x, camera_y)
        # Draw zombie projectiles
        GameRenderer.draw_zombie_projectiles(gs, game_ui, sprites, camera_x, camera_y)
        # --- end of to GameRenderer ---


        # --- TO GAMELOGIC ---
        # Game Updates
        GameLogic.on_shrine_check(gs, sounds, clock,game_ui)
        GameLogic.update_buffs(gs, gs.delta_time)
        # Draw XP orbs
        GameLogic.handle_xp_orbs(gs,game_ui.screen, camera_x, camera_y, game_ui.font, clock, sounds)
        # Draw health orbs
        GameLogic.handle_health_orbs(gs, game_ui.screen, camera_x, camera_y)
        # Combat system
        Combat.shoot_at_nearest_zombie(gs, pygame.time.get_ticks(), SHOT_COOLDOWN,sounds)
        # Spawning system
        Combat.continuous_spawn_system(gs, pygame.time.get_ticks(), BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE, 
                                                DIFFICULTY_INCREASE_INTERVAL, config.MAP_PIXEL_WIDTH, config.MAP_PIXEL_HEIGHT)
        # Update zombies positions and check for collisions or ranged attacks only handles logic not drawing
        GameLogic.update_zombie_positions(gs,pygame.time.get_ticks(), gs.delta_time)
        # Update zombie projectiles logic not drawing
        GameLogic.update_zombie_projectile_positions(gs, pygame.time.get_ticks(), gs.delta_time, config.MAP_PIXEL_WIDTH, config.MAP_PIXEL_HEIGHT)
        GameLogic.check_bullet_zombie_collisions(gs)
        # --- end of TO GAMELOGIC ---
        

        # --- to GameUI ---
        # Draw inventory
        game_ui.draw_inventory(gs.player.player_inventory)
        # Draw UI
        game_ui.draw_buffs(game_ui.screen, game_ui.font, game_ui.screen.get_width(), game_ui.screen.get_height() , gs.current_buffs)
        game_ui.draw_damage_flash()
        game_ui.draw_status_bars(gs.player)
        game_ui.draw_game_ui(game_ui.screen, game_ui.font, gs,
                     SHOT_COOLDOWN, pygame.time.get_ticks(), DIFFICULTY_INCREASE_INTERVAL, BASE_SPAWN_INTERVAL, SPAWN_RATE_INCREASE)
        # --- end of to GameUI ---
        
        #input handling
        keys_pressed = pygame.key.get_pressed()
        GameLogic.handle_player_input(keys_pressed, gs)
        
        pygame.display.flip()
        gs.delta_time = clock.tick(FPS) / 1000
    pygame.quit()

if __name__ == "__main__":
    main()
