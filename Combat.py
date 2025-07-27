# Combat.py - Combat system, shooting logic, and spawning
import math
import random
from Units import Bullet, Zombie

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

def shoot_at_nearest_zombie(player_pos, zombies, bullets, current_time, last_shot_time, shot_cooldown):

    if current_time - last_shot_time < shot_cooldown:
        return False, last_shot_time
    
    nearest_zombie = find_nearest_zombie(player_pos, zombies)
    if nearest_zombie:
        target_x = nearest_zombie.pos[0]
        target_y = nearest_zombie.pos[1]
        bullet = Bullet(player_pos[0], player_pos[1], target_x, target_y)
        bullets.append(bullet)
        last_shot_time = current_time
        return True, last_shot_time
    
    return False, last_shot_time

def update_bullets(bullets, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):

    for bullet in bullets[:]:  # Use slice copy to allow removal during iteration
        bullet.update(dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        if not bullet.active:
            bullets.remove(bullet)

def check_bullet_zombie_collisions(bullets, zombies):

    for bullet in bullets[:]:
        for zombie in zombies[:]:
            if bullet.check_collision_with_zombie(zombie):
                zombie.health -= bullet.damage
                bullet.active = False
                bullets.remove(bullet)
                
                if zombie.health <= 0:
                    zombies.remove(zombie)
                    print(f"Zombie killed! Remaining zombies: {len(zombies)}")
                break

def spawn_zombie_around_player(player_pos, zombies_count, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, min_distance=250, max_distance=400):

    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(min_distance, max_distance)
    
    zombie_x = player_pos[0] + math.cos(angle) * distance
    zombie_y = player_pos[1] + math.sin(angle) * distance
    
    zombie_x = max(50, min(MAP_PIXEL_WIDTH - 50, zombie_x))
    zombie_y = max(50, min(MAP_PIXEL_HEIGHT - 50, zombie_y))
    
    return Zombie(f"Zombie_{zombies_count}", zombie_x, zombie_y)

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
                          MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):
    
    current_spawn_interval = calculate_current_spawn_interval(current_time, game_start_time, 
                                                            base_spawn_interval, spawn_rate_increase, 
                                                            difficulty_increase_interval)
    
    if current_time - last_spawn_time >= current_spawn_interval:
        zombies_to_spawn = calculate_zombies_per_spawn(current_time, game_start_time, difficulty_increase_interval)
        
        for _ in range(zombies_to_spawn):
            new_zombie = spawn_zombie_around_player(player_pos, len(zombies), MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
            zombies.append(new_zombie)
        
        last_spawn_time = current_time
   
        time_elapsed = (current_time - game_start_time) / 1000
        print(f"Spawned {zombies_to_spawn} zombie(s) at {time_elapsed:.1f}s. Total zombies: {len(zombies)}")
        
        return last_spawn_time
    
    return last_spawn_time
