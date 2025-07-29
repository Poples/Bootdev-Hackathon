import pygame
import random
import PowerUpgrades
import math
from Units import Zombie
from PlayerInventory import XPOrb, HealthOrb


def initial_zomebie_spawn(gs, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):
    # Spawn initial zombies around the map
    for i in range(5):  # Start with 5 zombies
        # Spawn zombies in a circle around the player at a safe distance
        angle = (i / 5) * 2 * math.pi
        spawn_distance = 600  # pixels away from player
        zombie_x = gs.player.pos[0] + math.cos(angle) * spawn_distance
        zombie_y = gs.player.pos[1] + math.sin(angle) * spawn_distance
        # Ensure zombies spawn within map bounds
        zombie_x = max(50, min(MAP_PIXEL_WIDTH - 50, zombie_x))
        zombie_y = max(50, min(MAP_PIXEL_HEIGHT - 50, zombie_y))
        gs.zombies.append(Zombie(f"Zombie_{i}", zombie_x, zombie_y,"WalkerZombie"))

def update_buffs(gs, DELTA_TIME):
    # reduce buff durations:
    gs.current_buffs, buffs_to_remove = PowerUpgrades.update_buffs(gs.current_buffs, DELTA_TIME)
    for buff_name in buffs_to_remove:
        if buff_name == "Speed Boost":
            gs.player.speed = gs.player.speed - 2
        elif buff_name == "Pickup Radius":
            gs.player.pickup_radius = gs.player.pickup_radius - 5
            for orb in gs.xp_orbs:
                orb.pickup_radius = gs.player.pickup_radius
def get_tile_x_y(player, MG):
    tile_x = int(player.pos[0] // MG.TILE_SIZE)
    tile_y = int(player.pos[1] // MG.TILE_SIZE)
    return tile_x, tile_y

def on_shrine_check(GameState,MG,sounds, screen, font, clock):
    # Handle tile pickup logic
        tile_x, tile_y = get_tile_x_y(GameState.player, MG)

        has_picked_up = set() # Set to track which upgrade tiles have been picked up

        if 0 <= tile_x < MG.TILE_MAP_SIZE and 0 <= tile_y < MG.TILE_MAP_SIZE:
            current_tile = GameState.tile_map[tile_y][tile_x]
            if current_tile == 2:
                tile_key = (tile_x, tile_y)
                if tile_key not in has_picked_up:
                    has_picked_up.add(tile_key)
                    # Draw everything before pausing
                    pygame.display.flip()  # Show the last game frame
                    GameState.player.player_inventory.draw_inventory(screen, font)
                    sounds["Shrine"].play()
                    pause_start_time = pygame.time.get_ticks()
                    pygame.display.flip()  # Show the last game frame
                    if random.randint(1, 2) == 1:
                        PowerUpgrades.add_buff(GameState.current_buffs, "Speed Boost", 10)
                        GameState.player.speed = GameState.player.speed + 2
                        # Pause and show the random buff screen
                        PowerUpgrades.open_randombuff_screen(screen, font, screen.get_width(), screen.get_height(), " Extra Speed", 10)
                    else:
                        PowerUpgrades.add_buff(GameState.current_buffs, "Pickup Radius", 10)
                        GameState.player.pickup_radius = GameState.player.pickup_radius + 5
                        for orb in GameState.xp_orbs:
                            orb.pickup_radius = GameState.player.pickup_radius
                        # Pause and show the random buff screen
                        PowerUpgrades.open_randombuff_screen(screen, font, screen.get_width(), screen.get_height(), "Pickup Radius", 10)
                    clock.tick()  # Reset clock after pause
                    DELTA_TIME = 0
                    # After choosing upgrade, replace the tile
                    GameState.tile_map[tile_y][tile_x] = random.choice([0, 1])
                    
                    pause_duration = pygame.time.get_ticks() - pause_start_time
                    GameState.game_start_time = GameState.game_start_time + pause_duration

def handle_xp_orbs(gs, MG, screen, camera_x, camera_y, font, clock, sounds):
    tile_x, tile_y = get_tile_x_y(gs.player, MG)
    for orb in gs.xp_orbs[:]:
            if orb.check_collision_with_player(gs.player):
                orb.collected = True
                gs.xp_orbs.remove(orb)
                gs.player.player_inventory.add_item("XP", orb.value) #copy paste this line about 10 times for easy debug/testing

                sounds["OrbPickup"].play()
                if (gs.player.player_inventory.get_quantity("XP") >= 10 and gs.player.player_inventory.level < 10):
                    gs.player.player_inventory.level = gs.player.player_inventory.level + 1
                    gs.player.player_inventory.remove_item("XP", 10)
                    #logic for leveling up here
                    sounds["Levelup"].play()
                    pause_start_time = pygame.time.get_ticks()
                    pygame.display.flip()  # Show the last game frame
                    PowerUpgrades.open_levelup_screen(screen, gs.player, PowerUpgrades.apply_upgrade, font, screen.get_width(), screen.get_height())
                    clock.tick()  # Reset clock after pause
                    DELTA_TIME = 0
                    gs.tile_map[tile_y][tile_x] = random.choice([0, 1])
                    gs.pause_duration = pygame.time.get_ticks() - pause_start_time
                    gs.game_start_time = gs.game_start_time + gs.pause_duration
                    continue  # Skip the rest of the update this frame
            else:
                XPOrb.draw(orb, screen, camera_x, camera_y)

def handle_health_orbs(gs, screen, camera_x, camera_y):
    for orb in gs.health_orbs[:]:
            if orb.check_collision_with_player(gs.player):
                orb.collected = True
                gs.health_orbs.remove(orb)
                gs.player.gain_health(orb.value)
            else:
                orb.draw(screen, camera_x, camera_y)
        
# Update zombies positions and check for collisions or ranged attacks only handles logic not drawing
def update_zombie_positions(game_state,current_time, DELTA_TIME):
     for zombie in game_state.zombies:
            zombie.move_towards_player(game_state.player.pos, DELTA_TIME)
            if zombie.check_collision_with_player(game_state.player):
                zombie.attack_player(game_state.player, current_time)
            
            # Check if this is a ranged zombie and if it can shoot
            if hasattr(zombie, 'shoot_at_player'):  # Check if it's a RangedZombie
                projectile = zombie.shoot_at_player(game_state.player.pos, current_time)
                if projectile:
                    projectile.creation_time = current_time
                    game_state.zombie_projectiles.append(projectile)
#logic not drawing
def update_zombie_projectile_positions(game_state, current_time, DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):
    for projectile in game_state.zombie_projectiles[:]:
        projectile.update(DELTA_TIME, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, current_time)
        if not projectile.active:
            game_state.zombie_projectiles.remove(projectile)
        elif projectile.check_collision_with_player(game_state.player):
            game_state.player.take_damage(projectile.damage)
            projectile.active = False
            game_state.zombie_projectiles.remove(projectile)

def check_bullet_zombie_collisions(GameState):
    for bullet in GameState.bullets[:]:
        for zombie in GameState.zombies[:]:
            if bullet.check_collision_with_zombie(zombie):
                zombie.health -= bullet.damage
                bullet.active = False
                GameState.bullets.remove(bullet)
                
                if zombie.health <= 0:
                    GameState.zombies.remove(zombie)
                    if(random.randint(1, 10) == 1):
                        GameState.health_orbs.append(HealthOrb(zombie.pos[0], zombie.pos[1], GameState.player))
                    else:
                        GameState.xp_orbs.append(XPOrb(zombie.pos[0], zombie.pos[1], GameState.player))
                    print(f"Zombie killed! Remaining zombies: {len(GameState.zombies)}")
                break
