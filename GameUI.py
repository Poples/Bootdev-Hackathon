# GameUI.py - User interface and HUD elements
import pygame

def draw_game_ui(screen, font, player, zombies, bullets, current_time, last_shot_time, shot_cooldown,
                game_start_time, difficulty_increase_interval, base_spawn_interval, spawn_rate_increase,
                last_spawn_time):
    
    health_text = font.render(f"Health: {player.health}", True, (255, 0, 0))
    screen.blit(health_text, (10, screen.get_height() - 40))
    
    zombie_count_text = font.render(f"Zombies: {len(zombies)}", True, (255, 255, 255))
    screen.blit(zombie_count_text, (10, screen.get_height() - 70))
    
    bullet_count_text = font.render(f"Bullets: {len(bullets)}", True, (255, 255, 0))
    screen.blit(bullet_count_text, (10, screen.get_height() - 100))
    
    time_since_shot = current_time - last_shot_time
    if time_since_shot < shot_cooldown:
        cooldown_remaining = (shot_cooldown - time_since_shot) / 1000
        cooldown_text = font.render(f"Reload: {cooldown_remaining:.1f}s", True, (255, 165, 0))
        screen.blit(cooldown_text, (10, screen.get_height() - 130))
    
    time_elapsed = (current_time - game_start_time) / 1000
    time_text = font.render(f"Time: {time_elapsed:.1f}s", True, (0, 255, 255))
    screen.blit(time_text, (10, screen.get_height() - 160))
    
    difficulty_level = int(time_elapsed // (difficulty_increase_interval / 1000))
    difficulty_text = font.render(f"Difficulty: {difficulty_level + 1}", True, (255, 100, 255))
    screen.blit(difficulty_text, (10, screen.get_height() - 190))
    
    from Combat import calculate_current_spawn_interval
    current_spawn_interval = calculate_current_spawn_interval(current_time, game_start_time, 
                                                            base_spawn_interval, spawn_rate_increase, 
                                                            difficulty_increase_interval)
    time_since_spawn = current_time - last_spawn_time
    time_until_spawn = max(0, (current_spawn_interval - time_since_spawn) / 1000)
    spawn_timer_text = font.render(f"Next spawn: {time_until_spawn:.1f}s", True, (255, 255, 128))
    screen.blit(spawn_timer_text, (10, screen.get_height() - 220))

def draw_game_over_screen(screen, font, player):

    if player.health <= 0:
        game_over_text = font.render("GAME OVER! Press ESC to quit", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(game_over_text, game_over_rect)
        return True
    return False

def handle_player_input(keys, player, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, is_game_over, screen_rect):

    if is_game_over:
        if keys[pygame.K_ESCAPE]:
            return True  # Signal to quit game
    else:
        if keys[pygame.K_a]:
            player.move_left(dt, MAP_PIXEL_WIDTH)
        if keys[pygame.K_d]:
            player.move_right(dt, MAP_PIXEL_WIDTH)
        if keys[pygame.K_s]:
            player.move_down(dt, MAP_PIXEL_HEIGHT)
        if keys[pygame.K_w]:
            player.move_up(dt, MAP_PIXEL_HEIGHT)
        
        #player.movement_normalization(screen_rect)
        
    
    return False  # Don't quit game
