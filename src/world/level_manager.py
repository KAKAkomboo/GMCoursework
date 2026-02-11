import pygame
import random
from src.core.settings import tile_size

class Map:
    def __init__(self, mini_map_data):
        self.map_data = mini_map_data
        self.width = len(self.map_data[0]) * tile_size
        self.height = len(self.map_data) * tile_size

        self.textures = {
            0: self.create_texture((30, 80, 120)),  # Water
            1: self.create_texture((50, 120, 50)),  # Ground
            2: self.create_texture((130, 100, 80)), # Planks
            3: self.create_texture((100, 100, 100)),# Path
        }

        self.walkable_tiles = {
            0: False, # Water
            1: True,  # Ground
            2: True,  # Planks
            3: True,  # Path
        }

    def create_texture(self, color):
        s = pygame.Surface((tile_size, tile_size))
        s.fill(color)
        for _ in range(10):
            x = random.randint(0, tile_size-1)
            y = random.randint(0, tile_size-1)
            shade = random.randint(-15, 15)
            r, g, b = [max(0, min(255, c + shade)) for c in color]
            s.set_at((x, y), (r, g, b))
        return s

    def is_walkable(self, x, y):
        tile_x = int(x)
        tile_y = int(y)
        
        if not (0 <= tile_x < len(self.map_data[0]) and 0 <= tile_y < len(self.map_data)):
            return False
            
        tile_type = self.map_data[tile_y][tile_x]
        return self.walkable_tiles.get(tile_type, False)

    def draw(self, screen, camera_x, camera_y):
        start_col = max(0, camera_x // tile_size)
        end_col = min(len(self.map_data[0]), (camera_x + screen.get_width()) // tile_size + 2)
        start_row = max(0, camera_y // tile_size)
        end_row = min(len(self.map_data), (camera_y + screen.get_height()) // tile_size + 2)

        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                tile_type = self.map_data[y][x]
                texture = self.textures.get(tile_type)
                if texture:
                    screen.blit(texture, (x * tile_size - camera_x, y * tile_size - camera_y))
