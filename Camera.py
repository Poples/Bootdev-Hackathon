# Camera.py - Camera system for following the player
def update_camera(player_pos, screen_width, screen_height):
    
    camera_x = player_pos[0] - screen_width // 2
    camera_y = player_pos[1] - screen_height // 2
    return camera_x, camera_y

def get_screen_position(world_pos, camera_x, camera_y):

    screen_x = world_pos[0] - camera_x
    screen_y = world_pos[1] - camera_y
    return screen_x, screen_y

def get_map_offset(camera_x, camera_y):

    map_offset_x = -camera_x
    map_offset_y = -camera_y
    return map_offset_x, map_offset_y
