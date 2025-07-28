# Units.py - Contains all unit classes (Player, Zombie, Bullet)
import pygame
import math

class Unit:
    def __init__(self, name, pos_x, pos_y):
        self.name = name
        self.pos = [pos_x, pos_y]
        

class Player(Unit):
    def __init__(self, name, health, move_speed, pos_x, pos_y, atk_speed, player_image):
        super().__init__(name, pos_x, pos_y)
        #self.movement = pygame.math.Vector2(0,0)
        self.health = health
        self.image = player_image
        self.width, self.height = self.image.get_size()
        #self.rect = pygame.Rect(self.pos[0],self.pos[1], self.width, self.height)
        #self.pos = pygame.math.Vector2(self.rect)
        self.speed = move_speed
        self.pickup_radius = 5  # Default pickup radius
        self.atk_speed = atk_speed
        self.__hit_box = [
            self.pos[0] - (self.width * .5), 
            self.pos[1] - (self.height * .5), 
            self.pos[0] + (self.width * .5),
            self.pos[1] + (self.height * .5)
        ] # needs help

    # attribute modifications
    def take_damage(self, damage):
        self.health -= damage

    def gain_health(self, health_gained):
        self.health += health_gained
    
    def gain_move_speed(self, inc_move_speed):
        self.speed = self.speed * float(inc_move_speed)
    
    def gain_atk_speed(self, inc_atk_speed):
        self.atk_speed = self.atk_speed * float(inc_atk_speed)

    # Player Movement
    def move_left(self, dt, MAP_PIXEL_WIDTH):
        #self.movement.x = -1
        new_x = self.pos[0] - self.speed * dt
        print(new_x >= 0)
        if new_x >= 0:  # Check left boundary
            self.pos[0] = new_x

    def move_right(self, dt, MAP_PIXEL_WIDTH):
        #self.movement.x = 1
        new_x = self.pos[0] + self.speed * dt
        if new_x <= MAP_PIXEL_WIDTH:  # Check right boundary
            self.pos[0] = new_x

    def move_up(self, dt, MAP_PIXEL_HEIGHT):
        #self.movement.y = -1
        new_y = self.pos[1] - self.speed * dt
        if new_y >= 0:  # Check top boundary
            self.pos[1] = new_y

    def move_down(self, dt, MAP_PIXEL_HEIGHT):
        #self.movement.y = 1
        new_y = self.pos[1] + self.speed * dt
        if new_y <= MAP_PIXEL_HEIGHT:  # Check bottom boundary
            self.pos[1] = new_y
    
    #def movement_normalization(self, screen_rect):
        #if self.movement.length() > 0:
            #print(screen_rect, self.rect)
            #self.movement = self.movement.normalize() * self.speed
            #self.rect.clamp_ip(screen_rect)
            #self.pos += self.movement
            
            #self.movement = pygame.math.Vector2(0,0)


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

class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y, speed=500, damage=50):
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
