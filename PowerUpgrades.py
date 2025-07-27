# PowerUpgrades.py

import pygame

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
        pygame.display.flip()

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
