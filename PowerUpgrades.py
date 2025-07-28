# PowerUpgrades.py

import pygame
import main

BUTTON_WIDTH = 200   
BUTTON_HEIGHT = 300
BUTTON_SPACING = 40

power_options = ["Speed Boost", "Extra Health", "Fire Rate Up"]

def open_upgrade_screen(screen, player, apply_upgrade_callback, FONT, screen_width, screen_height):
    selected = False
    while not selected:
        # Optional: draw a semi-transparent overlay instead of full clear
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

        screen.blit(overlay, (0,0))

        draw_upgrade_options(screen, power_options, FONT, screen_width, screen_height)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                for i, option in enumerate(power_options):
                    rect = get_button_rect(i, screen_width, screen_height)
                    if rect.collidepoint(mouse_x, mouse_y):
                        apply_upgrade_callback(player, option)
                        selected = True
                        break
        
def get_button_rect(index, screen_width, screen_height):
    total_width = 3 * BUTTON_WIDTH + 2 * BUTTON_SPACING
    start_x = (screen_width - total_width) // 2
    x = start_x + index * (BUTTON_WIDTH + BUTTON_SPACING)
    y = (screen_height - BUTTON_HEIGHT) // 2
    return pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)

def draw_upgrade_options(screen, options, FONT, screen_width, screen_height):
    for i, option in enumerate(options):
        rect = get_button_rect(i, screen_width, screen_height)
        pygame.draw.rect(screen, (50, 50, 200), rect)
        pygame.draw.rect(screen, (255, 255, 255), rect, 2)

        text_surface = FONT.render(option, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def apply_upgrade(player, upgrade_type):
    if hasattr(player, "inventory"):
        player.inventory.add_item(upgrade_type, 1)
    print(f"Upgrade added to inventory: {upgrade_type}")
    if upgrade_type == "Fire Rate Up":
        player.gain_atk_speed(0.90)
    if upgrade_type == "Extra Health":
        player.gain_health(50)
    if upgrade_type == "Speed Boost":
        player.gain_move_speed(1.05)


def open_randombuff_screen(screen, FONT, screen_width, screen_height, buff_name, duration):
    selected = False

    # Set up OK button
    button_width, button_height = 200, 60
    button_rect = pygame.Rect(
        (screen_width - button_width) // 2,
        (screen_height - 120),
        button_width,
        button_height
    )

    while not selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_rect.collidepoint(event.pos):
                    selected = True

        # Darken background
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        screen.blit(overlay, (0, 0))

        # Buff info
        text = FONT.render(f"You got: {buff_name}", True, (255, 255, 255))
        duration_text = FONT.render(f"Duration: {int(duration)}s", True, (200, 200, 200))

        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
        duration_rect = duration_text.get_rect(center=(screen_width // 2, screen_height // 2))

        screen.blit(text, text_rect)
        screen.blit(duration_text, duration_rect)

        # OK button
        pygame.draw.rect(screen, (100, 220, 100), button_rect)
        pygame.draw.rect(screen, (255, 255, 255), button_rect, 2)

        button_text = FONT.render("OK", True, (0, 0, 0))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

        pygame.display.flip()

def update_buffs(current_buffs, dt):
    # dt = delta time elapsed since last update (seconds)
    updated_buffs = []
    buffs_to_remove = []
    for buff_name, time_left in current_buffs:
        time_left -= dt
        if time_left > 0:
            updated_buffs.append((buff_name, time_left))
        else:
            buffs_to_remove.append(buff_name)
            print(f"Buff {buff_name} expired")
    return updated_buffs, buffs_to_remove

def add_buff(current_buffs, buff_name, duration):
    current_buffs.append((buff_name, duration))

def draw_buffs(screen, FONT, screen_width, screen_height,buffs):
    for buff in buffs:
        buff_name, time_left = buff
        text_surface = FONT.render(f"{buff_name}: {time_left:.1f}s", True, (255, 255, 0))
        screen.blit(text_surface, (screen_width - 250, screen_height - 30 * (buffs.index(buff) + 1)))

def reset_player_buffs(player):
    player.speed = main.PLAYER_SPEED
    player.pickup_radius = main.PLAYER_PICKUP_RADIUS


    