# GameRenderer.py - Rendering system for all game objects
import pygame

def render_game_objects(screen, player, zombies, bullets, zombie_img, bullet_img, camera_x, camera_y):
    
    player_screen_x, player_screen_y = player.pos[0] - camera_x, player.pos[1] - camera_y
    screen.blit(player.image, (player_screen_x, player_screen_y))
    
    for zombie in zombies:
        zombie_screen_x = zombie.pos[0] - camera_x
        zombie_screen_y = zombie.pos[1] - camera_y
        screen.blit(zombie_img, (zombie_screen_x - zombie.width//2, zombie_screen_y - zombie.height//2))
    
    for bullet in bullets:
        bullet_screen_x = bullet.pos[0] - camera_x
        bullet_screen_y = bullet.pos[1] - camera_y
        
        screen.blit(bullet_img, (bullet_screen_x - bullet_img.get_width()//2, 
                                bullet_screen_y - bullet_img.get_height()//2))
