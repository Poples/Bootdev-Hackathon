# GameRenderer.py - Rendering system for all game objects
import pygame

def render_game_objects(screen, player, zombies, bullets, sprites, camera_x, camera_y):
    
    player_screen_x, player_screen_y = player.pos[0] - camera_x, player.pos[1] - camera_y
    screen.blit(player.image, player.img_rect)
    
    for zombie in zombies:
        zombie_screen_x = zombie.pos[0] - camera_x
        zombie_screen_y = zombie.pos[1] - camera_y
        if zombie.zombietype == "WalkerZombie":
            screen.blit(sprites["walker_zombie"], (zombie_screen_x - 32, zombie_screen_y - 32))
        elif zombie.zombietype == "TankZombie":
            screen.blit(sprites["tank_zombie"], (zombie_screen_x - 32, zombie_screen_y - 32))
        elif zombie.zombietype == "RangedZombie":
            screen.blit(sprites["ranged_zombie"], (zombie_screen_x - 32, zombie_screen_y - 32))
        else:
            screen.blit(sprites["walker_zombie"], (zombie_screen_x - 32, zombie_screen_y - 32))
    
    for bullet in bullets:
        bullet_screen_x = bullet.pos[0] - camera_x
        bullet_screen_y = bullet.pos[1] - camera_y
        screen.blit(sprites["bullet_img"], (bullet_screen_x - 24, bullet_screen_y - 24))

def update_bullets(bullets, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):

    for bullet in bullets[:]:  # Use slice copy to allow removal during iteration
        bullet.update(dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT)
        if not bullet.active:
            bullets.remove(bullet)

def draw_zombie_projectiles(gs, game_ui, sprites, camera_x, camera_y):
    for projectile in gs.zombie_projectiles:
            projectile.draw(game_ui.screen, camera_x, camera_y, sprites["zombie_spit"])