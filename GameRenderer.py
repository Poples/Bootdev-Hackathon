# GameRenderer.py - Rendering system for all game objects
import pygame

def render_game_objects(screen, player, zombies, bullets, sprites, camera_x, camera_y):
    
    player_screen_x, player_screen_y = player.pos[0] - camera_x, player.pos[1] - camera_y
    screen.blit(player.image, player.img_rect)
    
    for zombie in zombies:
        zombie_screen_x = zombie.pos[0] - camera_x
        zombie_screen_y = zombie.pos[1] - camera_y
        if zombie.zombietype == "WalkerZombie":
            screen.blit(sprites["walker_zombie"], (zombie_screen_x - zombie.width//2, zombie_screen_y - zombie.height//2))
        elif zombie.zombietype == "TankZombie":
            screen.blit(sprites["tank_zombie"], (zombie_screen_x - zombie.width//2, zombie_screen_y - zombie.height//2))
        else:
            # Default case if zombie type is unknown
            screen.blit(sprites["walker_zombie"], (zombie_screen_x - zombie.width//2, zombie_screen_y - zombie.height//2))
    
    for bullet in bullets:
        bullet_screen_x = bullet.pos[0] - camera_x
        bullet_screen_y = bullet.pos[1] - camera_y
        
        screen.blit(sprites["bullet_img"], (bullet_screen_x - sprites["bullet_img"].get_width()//2, 
                                bullet_screen_y - sprites["bullet_img"].get_height()//2))
