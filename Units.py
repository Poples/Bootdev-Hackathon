# Units.py - Contains all unit classes (Player, Zombie, Bullet)
import pygame
import math

class Unit:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.pos = [pos_x, pos_y]
        

class Player(Unit):
    def __init__(self, name, health,max_health, move_speed, atk_speed, player_image, player_start_pos):
        self.image = player_image
        self.img_rect = self.image.get_rect(center=player_start_pos)
        super().__init__(name, self.img_rect[0], self.img_rect[1])
        self.movement = pygame.math.Vector2(0,0)
        self.max_health = max_health
        self.health = health
        self.width = self.img_rect.width
        self.height = self.img_rect.height
        self.rect = pygame.Rect(self.pos[0],self.pos[1], self.width, self.height)
        self.pos = pygame.math.Vector2(self.pos)
        self.speed = move_speed
        self.pickup_radius = 5  # Default pickup radius
        self.atk_speed = atk_speed

    # attribute modifications
    def gain_max_health(self, max_health_gained):
        self.max_health += max_health_gained

    def take_damage(self, damage):
        self.health -= damage

    def gain_health(self, health_gained):
        self.health += health_gained
    
    def gain_move_speed(self, inc_move_speed):
        self.speed = self.speed * float(inc_move_speed)
    
    def gain_atk_speed(self, inc_atk_speed):
        self.atk_speed = self.atk_speed * float(inc_atk_speed)

    # Player Movement
    def move_left(self):
        self.movement.x = -1

    def move_right(self):
        self.movement.x = 1

    def move_up(self):
        self.movement.y = -1

    def move_down(self):
        self.movement.y = 1
    
    ### Normailzes diagonal movement while keeping players within mapS
    def movement_normalization(self, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):
        map_rect = pygame.Rect(0, 0, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT) #Gets map bounderies
        if self.movement.length() > 0:
            self.movement = self.movement.normalize() * self.speed
        self.rect.x += self.movement.x # moves player's rectangle sides
        self.rect.y += self.movement.y # moves player's rectangle top/bot
        self.rect.clamp_ip(map_rect)
        #self.pos += self.movement
        self.pos = pygame.math.Vector2(self.rect.center)
        self.movement = pygame.math.Vector2(0,0)


class Zombie(Unit):
    def __init__(self, name, pos_x, pos_y, zombietype, health=50, width=32, height=32, speed=50):
        super().__init__(name, pos_x, pos_y)
        self.zombietype = zombietype
        if zombietype == "WalkerZombie":
            self.health = 50
        elif zombietype == "TankZombie":
            self.health = 100
        else:
            self.health = health
        self.health = health
        self.width = width
        self.height = height
        self.speed = speed
        self.damage = 25
        self.last_damage_time = 0  
        self.damage_cooldown = 1000  # 1 second cooldown between damage deals (in milliseconds)
    
    def move_towards_player(self, player_pos, dt):
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            dx_normalized = dx / distance
            dy_normalized = dy / distance
            
            self.pos[0] += dx_normalized * self.speed * dt
            self.pos[1] += dy_normalized * self.speed * dt
    
    def check_collision_with_player(self, player):
        zombie_left = self.pos[0] - self.width // 2
        zombie_right = self.pos[0] + self.width // 2
        zombie_top = self.pos[1] - self.height // 2
        zombie_bottom = self.pos[1] + self.height // 2
        
        player_left = player.pos[0] - player.width // 2
        player_right = player.pos[0] + player.width // 2
        player_top = player.pos[1] - player.height // 2
        player_bottom = player.pos[1] + player.height // 2
        
        # Check if rectangles overlap
        return (zombie_left < player_right and 
                zombie_right > player_left and 
                zombie_top < player_bottom and 
                zombie_bottom > player_top)
    
    def attack_player(self, player, current_time):
        if current_time - self.last_damage_time >= self.damage_cooldown:
            player.take_damage(self.damage)
            self.last_damage_time = current_time
            print(f"Zombie hit player for {self.damage} damage! Player health: {player.health}")
            return True
        return False


class RangedZombie(Zombie):
    def __init__(self, name, pos_x, pos_y, health=75, width=32, height=32, speed=30):
        super().__init__(name, pos_x, pos_y, "RangedZombie", health, width, height, speed)
        self.attack_range = 300  # Distance at which zombie starts shooting
        self.projectile_speed = 200  # Speed of zombie projectiles
        self.projectile_damage = 15  # Damage per projectile
        self.last_shot_time = 0
        self.shot_cooldown = 2000  # 2 seconds between shots (in milliseconds)
        self.optimal_distance = 250  # Preferred distance from player
        self.retreat_threshold = 100  # Distance at which zombie retreats
        
    def move_towards_player(self, player_pos, dt):
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            dx_normalized = dx / distance
            dy_normalized = dy / distance
            
            # Ranged zombie behavior: maintain optimal distance
            if distance < self.retreat_threshold:
                # Too close - retreat
                self.pos[0] -= dx_normalized * self.speed * dt
                self.pos[1] -= dy_normalized * self.speed * dt
            elif distance > self.attack_range:
                # Too far - move closer
                self.pos[0] += dx_normalized * self.speed * dt
                self.pos[1] += dy_normalized * self.speed * dt
            elif distance > self.optimal_distance:
                # Move to optimal distance
                self.pos[0] += dx_normalized * self.speed * dt * 0.5  # Move slower when positioning
                self.pos[1] += dy_normalized * self.speed * dt * 0.5
    
    def can_shoot(self, player_pos, current_time):
        """Check if zombie can shoot at player"""
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        distance = (dx**2 + dy**2)**0.5
        
        # Can shoot if player is in range and cooldown has passed
        return (distance <= self.attack_range and 
                current_time - self.last_shot_time >= self.shot_cooldown)
    
    def shoot_at_player(self, player_pos, current_time):
        """Create a projectile aimed at the player"""
        if self.can_shoot(player_pos, current_time):
            self.last_shot_time = current_time
            return ZombieProjectile(self.pos[0], self.pos[1], player_pos[0], player_pos[1], 
                                  self.projectile_speed, self.projectile_damage)
        return None



class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y, speed=900, damage=50):
        self.pos = [start_x, start_y]
        self.speed = speed
        self.damage = damage
        
        # Calculate direction vector to target
        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            self.direction_x = dx / distance
            self.direction_y = dy / distance
        else:
            self.direction_x = 0
            self.direction_y = 0
        
        self.active = True
        self.width = 4  # Made the hitbox smaller cause it was hitting the zombie from 20 pixels away
        self.height = 4
    
    def update(self, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT):
        if self.active:
            self.pos[0] += self.direction_x * self.speed * dt
            self.pos[1] += self.direction_y * self.speed * dt
            
            # Check if bullet is out of bounds
            if (self.pos[0] < -50 or self.pos[0] > MAP_PIXEL_WIDTH + 50 or
                self.pos[1] < -50 or self.pos[1] > MAP_PIXEL_HEIGHT + 50):
                self.active = False
    
    def check_collision_with_zombie(self, zombie):
        if not self.active:
            return False
            

        collision_padding = 4  # Reduced collision box by 4 pixels on each side: Needs more testing
        
        bullet_left = self.pos[0] - self.width // 2
        bullet_right = self.pos[0] + self.width // 2
        bullet_top = self.pos[1] - self.height // 2
        bullet_bottom = self.pos[1] + self.height // 2
        
        zombie_left = zombie.pos[0] - (zombie.width // 2) + collision_padding
        zombie_right = zombie.pos[0] + (zombie.width // 2) - collision_padding
        zombie_top = zombie.pos[1] - (zombie.height // 2) + collision_padding
        zombie_bottom = zombie.pos[1] + (zombie.height // 2) - collision_padding
        
        return (bullet_left < zombie_right and 
                bullet_right > zombie_left and 
                bullet_top < zombie_bottom and 
                bullet_bottom > zombie_top)
    

class ZombieProjectile:
    def __init__(self, start_x, start_y, target_x, target_y, speed=200, damage=15):
        self.pos = [start_x, start_y]
        self.speed = speed
        self.damage = damage
        
        # Calculate direction vector to target
        dx = target_x - start_x
        dy = target_y - start_y
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            self.direction_x = dx / distance
            self.direction_y = dy / distance
        else:
            self.direction_x = 0
            self.direction_y = 0
        
        self.active = True
        self.width = 8
        self.height = 8
        self.lifetime = 3000  # 3 seconds max lifetime
        self.creation_time = 0  # Will be set when created
    
    def update(self, dt, MAP_PIXEL_WIDTH, MAP_PIXEL_HEIGHT, current_time):
        if self.active:
            self.pos[0] += self.direction_x * self.speed * dt
            self.pos[1] += self.direction_y * self.speed * dt
            
            # Check if projectile is out of bounds or expired
            if (self.pos[0] < -50 or self.pos[0] > MAP_PIXEL_WIDTH + 50 or
                self.pos[1] < -50 or self.pos[1] > MAP_PIXEL_HEIGHT + 50 or
                current_time - self.creation_time > self.lifetime):
                self.active = False
    
    def draw(self, screen, camera_x, camera_y, spit_sprite):
        """Draw the projectile using the spit sprite"""
        if self.active:
            projectile_screen_x = self.pos[0] - camera_x
            projectile_screen_y = self.pos[1] - camera_y
            
            # Center the sprite on the projectile position
            sprite_x = projectile_screen_x - spit_sprite.get_width() // 2
            sprite_y = projectile_screen_y - spit_sprite.get_height() // 2
            
            screen.blit(spit_sprite, (sprite_x, sprite_y))
    
    def check_collision_with_player(self, player):
        if not self.active:
            return False
        
        projectile_left = self.pos[0] - self.width // 2
        projectile_right = self.pos[0] + self.width // 2
        projectile_top = self.pos[1] - self.height // 2
        projectile_bottom = self.pos[1] + self.height // 2
        
        player_left = player.pos[0] - player.width // 2
        player_right = player.pos[0] + player.width // 2
        player_top = player.pos[1] - player.height // 2
        player_bottom = player.pos[1] + player.height // 2
        
        return (projectile_left < player_right and 
                projectile_right > player_left and 
                projectile_top < player_bottom and 
                projectile_bottom > player_top)