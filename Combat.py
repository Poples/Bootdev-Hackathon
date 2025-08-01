# Combat.py - Combat system, shooting logic, and spawning
import math
import random
from Units import Bullet, Zombie, RangedZombie
from PlayerInventory import XPOrb, HealthOrb

def find_nearest_zombie(player_pos, zombies):
    
    if not zombies:
        return None
    
    nearest_zombie = None
    min_distance = float('inf')
    
    for zombie in zombies:
        dx = zombie.pos[0] - player_pos[0]
        dy = zombie.pos[1] - player_pos[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance < min_distance:
            min_distance = distance
            nearest_zombie = zombie
    
    return nearest_zombie

def shoot_at_nearest_zombie(player, zombies, bullets, current_time, last_shot_time, shot_cooldown):

    if current_time - last_shot_time < shot_cooldown * player.atk_speed:
        return False, last_shot_time
    
    nearest_zombie = find_nearest_zombie(player.pos, zombies)
    if nearest_zombie:
        target_x = nearest_zombie.pos[0]
        target_y = nearest_zombie.pos[1]
        bullet = Bullet(player.pos[0], player.pos[1], target_x, target_y)
        bullets.append(bullet)
        last_shot_time = current_time
        return True, last_shot_time
    
    return False, last_shot_time

def update_bullets(bullets, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):

    for bullet in bullets[:]:  # Use slice copy to allow removal during iteration
        bullet.update(dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        if not bullet.active:
            bullets.remove(bullet)

def check_bullet_zombie_collisions(player, bullets, zombies,xp_orbs,health_orbs):

    for bullet in bullets[:]:
        for zombie in zombies[:]:
            if bullet.check_collision_with_zombie(zombie):
                zombie.health -= bullet.damage
                bullet.active = False
                bullets.remove(bullet)
                
                if zombie.health <= 0:
                    zombies.remove(zombie)
                    if(random.randint(1, 10) == 1):
                        health_orbs.append(HealthOrb(zombie.pos[0], zombie.pos[1], player))
                    else:
                        xp_orbs.append(XPOrb(zombie.pos[0], zombie.pos[1], player))
                    print(f"Zombie killed! Remaining zombies: {len(zombies)}")
                break

def spawn_zombie_around_player(zombietype,player_pos, zombies_count, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, min_distance=500, max_distance=1000):

    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(min_distance, max_distance)
    
    zombie_x = player_pos[0] + math.cos(angle) * distance
    zombie_y = player_pos[1] + math.sin(angle) * distance
    
    zombie_x = max(50, min(MAP_PIXEL_WIDTH - 50, zombie_x))
    zombie_y = max(50, min(MAP_PIXEL_HEIGHT - 50, zombie_y))
    
    if zombietype == "WalkerZombie":
        return Zombie(f"Zombie_{zombies_count}", zombie_x, zombie_y, "WalkerZombie")
    elif zombietype == "TankZombie":
        return Zombie(f"Zombie_{zombies_count}", zombie_x, zombie_y, "TankZombie" , health=100)
    else:
        return Zombie(f"Zombie_{zombies_count}", zombie_x, zombie_y, "WalkerZombie")

def calculate_current_spawn_interval(game_time, game_start_time, base_spawn_interval, spawn_rate_increase, difficulty_increase_interval):

    time_elapsed = game_time - game_start_time
    difficulty_level = int(time_elapsed // difficulty_increase_interval)
    
    current_interval = max(500, base_spawn_interval * (spawn_rate_increase ** difficulty_level))
    return current_interval

def calculate_zombies_per_spawn(game_time, game_start_time, difficulty_increase_interval):

    time_elapsed = game_time - game_start_time
    difficulty_level = int(time_elapsed // difficulty_increase_interval)
    
    return min(3, 1 + difficulty_level // 2)

def continuous_spawn_system(player_pos, zombies, current_time, last_spawn_time, game_start_time, 
                          base_spawn_interval, spawn_rate_increase, difficulty_increase_interval, 
                          MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT,player_inventory):
    
    
    current_spawn_interval = calculate_current_spawn_interval(current_time, game_start_time, 
                                                            base_spawn_interval, spawn_rate_increase, 
                                                            difficulty_increase_interval)
    
    if current_time - last_spawn_time >= current_spawn_interval:
        zombies_to_spawn = calculate_zombies_per_spawn(current_time, game_start_time, difficulty_increase_interval)
        
        for _ in range(zombies_to_spawn):
            # Determine zombie type based on difficulty level
            time_elapsed = current_time - game_start_time
            difficulty_level = int(time_elapsed // difficulty_increase_interval)
            
            # Spawn probabilities based on difficulty
            if difficulty_level < 1:
                # Early game: only walker zombies
                zombie_type = "WalkerZombie"
            elif difficulty_level < 3:
                # Mid game: mostly walkers, some tanks
                zombie_type = random.choice(["WalkerZombie", "WalkerZombie", "WalkerZombie", "TankZombie"])
            else:
                # Late game: walkers, tanks, and ranged zombies
                zombie_type = random.choice([
                    "WalkerZombie", "WalkerZombie", 
                    "TankZombie", "TankZombie",
                    "RangedZombie"
                ])
            
            # Create the appropriate zombie type
            if zombie_type == "RangedZombie":
                new_zombie = spawn_ranged_zombie_around_player(player_pos, len(zombies), 
                                                             MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
            else:
                new_zombie = spawn_zombie_around_player(zombie_type, player_pos, len(zombies), 
                                                       MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
            
            if new_zombie:
                zombies.append(new_zombie)
        
        return current_time
    
    return last_spawn_time



def spawn_ranged_zombie_around_player(player_pos, zombies_count, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, 
                                     min_distance=500, max_distance=1000):

    
    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(min_distance, max_distance)
    
    zombie_x = player_pos[0] + math.cos(angle) * distance
    zombie_y = player_pos[1] + math.sin(angle) * distance
    
    zombie_x = max(64, min(MAP_PIXEL_WIDTH - 64, zombie_x))
    zombie_y = max(64, min(MAP_PIXEL_HEIGHT - 64, zombie_y))
 
    new_zombie = RangedZombie(f"RangedZombie_{zombies_count}", zombie_x, zombie_y, 
                             health=75, width=64, height=64, speed=30)
    return new_zombie
