import pygame
from Camera import get_screen_position

class PlayerInventory:
    def __init__(self):
        # Store items as a dictionary: {item_name: quantity}
        self.items = {}
        self.picked_up_tiles = set()  # stores (tile_x, tile_y) coords of upgrade tiles used

    def add_item(self, item_name, quantity=1):
        if item_name in self.items:
            self.items[item_name] += quantity
        else:
            self.items[item_name] = quantity

    def remove_item(self, item_name, quantity=1):
        if item_name in self.items:
            self.items[item_name] -= quantity
            if self.items[item_name] <= 0:
                del self.items[item_name]
            return True
        return False  # Item not found

    def has_item(self, item_name):
        return item_name in self.items

    def get_quantity(self, item_name):
        return self.items.get(item_name, 0)

    def list_items(self):
        return self.items.copy()  # return a copy to prevent external modification
    

    def draw_inventory(self, screen, font):
        x, y = 10, 10  # top-left corner
        for item, quantity in self.items.items():
            text = f"{item}: {quantity}"
            text_surface = font.render(text, True, (255, 255, 0))
            screen.blit(text_surface, (x, y))
            y += 20  # spacing between lines

class XPOrb:
    def __init__(self, x, y, pickup_radius=5, value = 1 ):
        self.pos = [x, y]
        self.pickup_radius = pickup_radius
        self.value = value
        self.image = pygame.image.load("assets/XPOrbSprite.png")
        self.collected = False

    def draw(self, screen, camera_x, camera_y):
        screen_x, screen_y = get_screen_position(self.pos, camera_x, camera_y)
        screen.blit(self.image, (screen_x, screen_y))

    def check_collision_with_player(self, player):
        player_x, player_y = player.pos
        dx = player_x - self.pos[0]
        dy = player_y - self.pos[1]
        distance = (dx**2 + dy**2)**0.5
        return distance <= self.pickup_radius * self.pickup_radius