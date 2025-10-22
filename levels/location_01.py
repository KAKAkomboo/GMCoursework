import pygame
from Settings import tile_size
class Map:
    def __init__(self, mini_map):
        self.mini_map = mini_map
        self.width = len(mini_map[0]) * tile_size
        self.height = len(mini_map) * tile_size

        self.tile_colors = {
            1: (100, 100, 100),
            0: (0, 0, 0),
            2: (0, 255, 0),
            3: (255, 255, 0),
            4: (0, 0, 255),
            5: (255, 0, 0),
        }

    def draw(self, screen, camera_x, camera_y):
        for y, row in enumerate(self.mini_map):
            for x, tile in enumerate(row):
                tile_type = tile if isinstance(tile, int) else 0
                color = self.tile_colors.get(tile_type, (0, 0, 0))
                rect = pygame.Rect(x * tile_size - camera_x, y * tile_size - camera_y, tile_size, tile_size)
                pygame.draw.rect(screen, color, rect)
    def is_walkable(self, x, y):

        if 0 <= y < len(self.mini_map) and 0 <= x < len(self.mini_map[0]):
            tile = self.mini_map[y][x]
            return tile != 1
        return False