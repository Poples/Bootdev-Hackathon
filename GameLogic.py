import pygame
import random
import PowerUpgrades
import math
from Units import Zombie
from PlayerInventory import XPOrb


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
def on_shrine_check(player,MG,sounds, tile_map, xp_orbs, player_inventory, current_buffs, screen, font, clock, game_start_time):
    # Handle tile pickup logic
        
        tile_x, tile_y = get_tile_x_y(player, MG)

        has_picked_up = set() # Set to track which upgrade tiles have been picked up


        if 0 <= tile_x < MG.TILE_MAP_SIZE and 0 <= tile_y < MG.TILE_MAP_SIZE:
            current_tile = tile_map[tile_y][tile_x]
            if current_tile == 2:
                tile_key = (tile_x, tile_y)
                if tile_key not in has_picked_up:
                    has_picked_up.add(tile_key)
                    # Draw everything before pausing
                    pygame.display.flip()  # Show the last game frame
                    player.player_inventory.draw_inventory(screen, font)
                    sounds["Shrine"].play()
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

def handle_xp_orbs(gs,MG, screen, camera_x, camera_y, font, clock, sounds):
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