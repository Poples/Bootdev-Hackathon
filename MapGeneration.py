# MapGeneration.py
import random
import pygame

TILE_MAP_SIZE = 50
TILE_SIZE = 64

tile_colors = {
    0: (34, 139, 34),   # grass
    1: (139, 69, 19),   # dirt
    2: (128, 128, 128),   # upgrade station (cyan)
    3: (0, 0, 0)  # black for unknown tiles
}
# Load tree sprite once
tree_sprite = pygame.image.load("assets/TreeSprite.png")
tree_sprite = pygame.transform.scale(tree_sprite, (TILE_SIZE, TILE_SIZE))

rock_sprite = pygame.image.load("assets/RockSprite.png")
rock_sprite = pygame.transform.scale(rock_sprite, (TILE_SIZE, TILE_SIZE))

shrine_sprite = pygame.image.load("assets/ShrineSprite.png")
shrine_sprite = pygame.transform.scale(shrine_sprite, (TILE_SIZE, TILE_SIZE))

wall_sprite = pygame.image.load("assets/WallSprite.png")
wall_sprite = pygame.transform.scale(wall_sprite, (TILE_SIZE, TILE_SIZE))


tree_positions = set()
rock_positions = set()

def generate_tile_map():
    global tree_positions, rock_positions
    tile_map = []
    for row_index in range(TILE_MAP_SIZE):
        row = []
        for col_index in range(TILE_MAP_SIZE):
            if row_index == 0 or row_index == TILE_MAP_SIZE - 1 or col_index == 0 or col_index == TILE_MAP_SIZE - 1:
                tile = 3  # wall
            else:
                roll = random.randint(1, 200)
                if roll == 1:
                    tile = 2  # upgrade
                else:
                    tile = random.choice([0, 1])  # grass or dirt
                # 1 in 10 chance for tree on grass
                if tile == 0 and random.randint(1, 10) == 1:
                    tree_positions.add((row_index, col_index))
                # 1 in 10 chance for rock on dirt
                if tile == 1 and random.randint(1, 10) == 1:
                    rock_positions.add((row_index, col_index))
            row.append(tile)
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
            if tile ==3:
                screen.blit(wall_sprite, tile_rect.topleft)
            elif (row_index, col_index) in tree_positions:
                screen.blit(tree_sprite, tile_rect.topleft)
            elif (row_index, col_index) in rock_positions:
                screen.blit(rock_sprite, tile_rect.topleft)
            elif tile == 2:
                screen.blit(shrine_sprite, tile_rect.topleft)

def get_tile_coordinates_from_position(pos, offset_x, offset_y):
    tile_x = int((pos[0] - offset_x) // TILE_SIZE)
    tile_y = int((pos[1] - offset_y) // TILE_SIZE)
    return tile_x, tile_y
