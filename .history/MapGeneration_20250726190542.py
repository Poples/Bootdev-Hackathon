# MapGeneration.py
import random
import pygame

TILE_MAP_SIZE = 20
TILE_SIZE = 64

tile_colors = {
    0: (34, 139, 34),   # grass
    1: (139, 69, 19),   # dirt
    2: (0, 255, 255)   # upgrade station (cyan)
}
# Load tree sprite once
tree_sprite = pygame.image.load("assets/TreeSprite.png")
tree_sprite = pygame.transform.scale(tree_sprite, (TILE_SIZE, TILE_SIZE))

rock_sprite = pygame.image.load("assets/RockSprite.png")
rock_sprite = pygame.transform.scale(rock_sprite, (TILE_SIZE, TILE_SIZE))

def generate_tile_map():
    tile_map = []
    for _ in range(TILE_MAP_SIZE):
        row = []
        for _ in range(TILE_MAP_SIZE):
            # 1 in 15 chance for upgrade station (2), else 0 (grass) or 1 (dirt)
            roll = random.randint(1, 15)
            if roll == 1:
                row.append(2)
            else:
                row.append(random.choice([0, 1]))
        tile_map.append(row)
    return tile_map

def draw_tile_map(screen, tile_map, offset_x, offset_y):
    for row_index, row in enumerate(tile_map):
        for col_index, tile in enumerate(row):
            tile_color = tile_colors.get(tile, (0, 0, 0))
            tile_rect = pygame.Rect(
                offset_x + col_index * TILE_SIZE,
                offset_y + row_index * TILE_SIZE,
                TILE_SIZE,
                TILE_SIZE
            )
            pygame.draw.rect(screen, tile_color, tile_rect)
            if tile==0:
                screen.blit(tree_sprite, tile_rect.topleft)
            if tile==1:
                screen.blit(rock_sprite, tile_rect.topleft)
def get_tile_coordinates_from_position(pos, offset_x, offset_y):
    tile_x = int((pos[0] - offset_x) // TILE_SIZE)
    tile_y = int((pos[1] - offset_y) // TILE_SIZE)
    return tile_x, tile_y
