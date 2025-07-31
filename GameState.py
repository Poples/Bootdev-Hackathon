import pygame

class GameState:

    def __init__(self):
        
        delta_time = 0
        # Core entities
        self.player = None
        self.zombies = []
        self.bullets = []
        self.zombie_projectiles = []

        # Resources
        self.xp_orbs = []
        self.health_orbs = []

        # Background Map
        self.tile_map = None
        self.shrine_pickups = set()


        self.last_shot_time = 0
        self.last_spawn_time = 0
        self.game_start_time = 0
        self.pause_duration = 0
        self.pause_start_time = 0
        self.game_ended_time = 0

        self.running = True
        self.paused = False
        self.game_over = False

        self.player_inventory = None
        self.current_buffs = []
        
        self.clock = None
        self.game_start_time = 0
        self.delta_time = 0
        
    def toggle_pause(self):
        now = pygame.time.get_ticks()
        if not self.paused:
            self.paused = True
            self.pause_start_time = now
        else:
            self.paused = False
            self.pause_duration = now - self.pause_start_time
            self.game_start_time += self.pause_duration