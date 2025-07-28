# GameUI.py - User interface and HUD elements
import pygame

def draw_game_ui(screen, font, player, zombies, bullets, current_time, last_shot_time, shot_cooldown,
                game_start_time, difficulty_increase_interval, base_spawn_interval, spawn_rate_increase,
                last_spawn_time):

    health_text = font.render(f"Health: {player.health}", True, (255, 0, 0))
    screen.blit(health_text, (10, screen.get_height() - 40))
    
    zombie_count_text = font.render(f"Zombies: {len(zombies)}", True, (255, 255, 255))
    screen.blit(zombie_count_text, (10, screen.get_height() - 70))
    
    bullet_count_text = font.render(f"attack speed: {player.atk_speed}", True, (255, 255, 0))
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

def handle_player_input(keys, player, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, is_game_over):

    if is_game_over:
        if keys[pygame.K_ESCAPE]:
            return True  # Signal to quit game
    else:
        if keys[pygame.K_a]:
            player.move_left()
        if keys[pygame.K_d]:
            player.move_right()
        if keys[pygame.K_s]:
            player.move_down()
        if keys[pygame.K_w]:
            player.move_up()
        
        # Apply normalized movement with boundary checking
        player.movement_normalization(MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        
    
    return False  # Don't quit game


def draw_status_bars(screen, font, player, player_inventory):
    # Constants
    bar_width = 200
    bar_height = 20
    spacing = 400
    top_margin = 10
    screen_width = screen.get_width()

    # Health bar
    #health_ratio = player.health / player.max_health
    #health_bar_rect = pygame.Rect(screen_width // 2 - bar_width - spacing, top_margin, bar_width, bar_height)
    #pygame.draw.rect(screen, (100, 0, 0), health_bar_rect)  # Dark red background
    #pygame.draw.rect(screen, (255, 0, 0), (health_bar_rect.x, health_bar_rect.y, bar_width * health_ratio, bar_height))
#
    ## Health label
    #health_text = font.render("Health", True, (255, 255, 255))
    #screen.blit(health_text, (health_bar_rect.centerx - health_text.get_width() // 2, health_bar_rect.y + bar_height + 2))

    # XP bar
    xp = player.player_inventory.get_quantity("XP")
    xp_ratio = min(xp / 10, 1)
    xp_bar_rect = pygame.Rect(screen_width // 2 - spacing, top_margin, bar_width, bar_height)
    pygame.draw.rect(screen, (50, 0, 50), xp_bar_rect)  # Dark purple background
    pygame.draw.rect(screen, (160, 32, 240), (xp_bar_rect.x, xp_bar_rect.y, bar_width * xp_ratio, bar_height))

    # XP label
    xp_text = font.render("XP", True, (255, 255, 255))
    screen.blit(xp_text, (xp_bar_rect.centerx - xp_text.get_width() // 2, xp_bar_rect.y + bar_height + 2))

def draw_pause_menu(screen, font):

    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    title_text = font.render("GAME PAUSED", True, (255, 255, 255))
    resume_text = font.render("Press ESC to Resume", True, (255, 255, 255))
    quit_text = font.render("Press Q to Quit", True, (255, 255, 255))
    
    screen_center_x = screen.get_width() // 2
    screen_center_y = screen.get_height() // 2
    
    title_rect = title_text.get_rect(center=(screen_center_x, screen_center_y - 60))
    resume_rect = resume_text.get_rect(center=(screen_center_x, screen_center_y))
    quit_rect = quit_text.get_rect(center=(screen_center_x, screen_center_y + 40))
    
    screen.blit(title_text, title_rect)
    screen.blit(resume_text, resume_rect)
    screen.blit(quit_text, quit_rect)
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_q]:
        return "quit"
    
    return None