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
    def __init__(self, map_data_dict=None):
        if map_data_dict:
            self.layer_water = [[Tile(cell) for cell in row] for row in map_data_dict["water"]]

            self.layer_ground = []
            for row in map_data_dict["ground"]:
                new_row = []
                for cell in row:
                    new_row.append(Tile(cell) if cell is not None else None)
                self.layer_ground.append(new_row)

            self.layer_objects = []
            for row in map_data_dict["objects"]:
                new_row = []
                for cell in row:
                    new_row.append(Tile(cell) if cell is not None else None)
                self.layer_objects.append(new_row)

            self.width_tiles = len(self.layer_water[0])
            self.height_tiles = len(self.layer_water)
        else:

            self.width_tiles = 20
            self.height_tiles = 20
            self.layer_water = [[Tile(0) for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
            self.layer_ground = [[None for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]
            self.layer_objects = [[None for _ in range(self.width_tiles)] for _ in range(self.height_tiles)]

        self.width = self.width_tiles * tile_size
        self.height = self.height_tiles * tile_size

        self.textures = {}
        self.load_textures()

    def load_textures(self):
        def get_texture(path, fallback_color):
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    return pygame.transform.scale(img, (tile_size, tile_size))
                except:
                    pass
            return self.create_texture(fallback_color)

        self.textures[0] = get_texture("src/assets/textures/ground/water.png", (20, 30, 70))
        self.textures[1] = get_texture("src/assets/textures/ground/grass.png", (50, 60, 40))
        self.textures[2] = get_texture("src/assets/textures/blocks/wood.png", (130, 110, 90))
        self.textures[3] = get_texture("src/assets/textures/ground/path.png", (80, 70, 60))
        self.textures[4] = get_texture("src/assets/textures/ground/wather_grass.png", (30, 45, 55))

        self.textures[5] = self.create_texture((20, 50, 20))
        self.textures[6] = self.create_texture((100, 80, 60))

        self.textures[9] = self.create_texture((255, 0, 255))

    def create_texture(self, color):
        s = pygame.Surface((tile_size, tile_size))
        s.fill(color)
        s.set_alpha(100)
        return s

    def is_walkable(self, x, y):
        tile_x = int(x)
        tile_y = int(y)
        if not (0 <= tile_x < self.width_tiles and 0 <= tile_y < self.height_tiles):
            return False

        if self.layer_objects[tile_y][tile_x]:
            return False

        ground_tile = self.layer_ground[tile_y][tile_x]
        if ground_tile:
            return ground_tile.type in [1, 2, 3, 9]

        return False

    def check_trigger(self, x, y):
        tile_x = int(x)
        tile_y = int(y)
        if 0 <= tile_x < self.width_tiles and 0 <= tile_y < self.height_tiles:
            ground_tile = self.layer_ground[tile_y][tile_x]
            if ground_tile and ground_tile.type == 9:
                return True
        return False

    def draw(self, screen, camera_x, camera_y):
        start_col = max(0, camera_x // tile_size)
        end_col = min(self.width_tiles, (camera_x + screen.get_width()) // tile_size + 2)
        start_row = max(0, camera_y // tile_size)
        end_row = min(self.height_tiles, (camera_y + screen.get_height()) // tile_size + 2)

        for y in range(start_row, end_row):
            for x in range(start_col, end_col):

                water_tile = self.layer_water[y][x]
                screen.blit(self.textures[water_tile.type], (x * tile_size - camera_x, y * tile_size - camera_y))

                ground_tile = self.layer_ground[y][x]
                if ground_tile:
                    screen.blit(self.textures[ground_tile.type], (x * tile_size - camera_x, y * tile_size - camera_y))

                obj_tile = self.layer_objects[y][x]
                if obj_tile:
                    screen.blit(self.textures[obj_tile.type], (x * tile_size - camera_x, y * tile_size - camera_y))
