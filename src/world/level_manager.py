import pygame
import random
import math
import os
from src.core.settings import tile_size

class Tile:
    def __init__(self, tile_type, height=0):
        self.type = tile_type 
        self.height = height
        self.building_id = None 

class Map:
    def __init__(self, mini_map_data=None):
        if mini_map_data:
            self.map_data = [[Tile(cell) for cell in row] for row in mini_map_data]
            self.width_tiles = len(mini_map_data[0])
            self.height_tiles = len(mini_map_data)
        else:
            self.width_tiles = 100
            self.height_tiles = 120
            self.map_data = [[Tile(0) for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
            self.generate_map()
        
        self.width = self.width_tiles * tile_size
        self.height = self.height_tiles * tile_size
        
        self.textures = {}
        self.load_textures()

    def load_textures(self):
        def get_texture(path, fallback_color):
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    return pygame.transform.scale(img, (tile_size, tile_size))
                except:
                    pass
            return self.create_texture(fallback_color)

        self.textures[0] = get_texture("src/assets/textures/ground/water.png", (20, 30, 70))

        self.textures[1] = get_texture("src/assets/textures/ground/grass.png", (50, 60, 40))

        self.textures[2] = get_texture("src/assets/textures/blocks/wood.png", (130, 110, 90))

        self.textures[3] = get_texture("src/assets/textures/ground/path.png", (80, 70, 60))

        self.textures[4] = get_texture("src/assets/textures/ground/wather_grass.png", (30, 45, 55))

    def create_texture(self, color):
        s = pygame.Surface((tile_size, tile_size))
        s.fill(color)
        for _ in range(15):
            x, y = random.randint(0, tile_size-1), random.randint(0, tile_size-1)
            shade = random.randint(-15, 15)
            r, g, b = [max(0, min(255, c + shade)) for c in color]
            s.set_at((x, y), (r, g, b))
        return s

    def generate_map(self):
        pass

    def is_walkable(self, x, y):
        tile_x = int(x)
        tile_y = int(y)
        if not (0 <= tile_x < self.width_tiles and 0 <= tile_y < self.height_tiles):
            return False
        tile_type = self.map_data[tile_y][tile_x].type

        return tile_type in [1, 2, 3]

    def draw(self, screen, camera_x, camera_y):
        start_col = max(0, camera_x // tile_size)
        end_col = min(self.width_tiles, (camera_x + screen.get_width()) // tile_size + 2)
        start_row = max(0, camera_y // tile_size)
        end_row = min(self.height_tiles, (camera_y + screen.get_height()) // tile_size + 2)

        for y in range(start_row, end_row):
            for x in range(start_col, end_col):
                tile = self.map_data[y][x]
                texture = self.textures.get(tile.type, self.textures[0])
                screen.blit(texture, (x * tile_size - camera_x, y * tile_size - camera_y))
