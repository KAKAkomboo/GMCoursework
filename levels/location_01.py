# levels/location_01.py
import pygame
from typing import List, Optional, Tuple
from Settings import tile_size

class Map:

    DEFAULT_TILE_COLORS = {
        0: (40, 40, 40),    # floor
        1: (100, 100, 100), # wall
        2: (0, 255, 0),
        3: (255, 255, 0),
        4: (0, 0, 255),
        5: (255, 0, 0),
    }

    def __init__(self, mini_map: List[List[int]], tile_colors: Optional[dict] = None):
        self.mini_map = mini_map
        self.tile_width = len(mini_map[0]) if mini_map and mini_map[0] else 0
        self.tile_height = len(mini_map)
        self.width = self.tile_width * tile_size
        self.height = self.tile_height * tile_size

        self.tile_colors = dict(self.DEFAULT_TILE_COLORS)
        if tile_colors:
            self.tile_colors.update(tile_colors)

    def in_bounds(self, tx: int, ty: int) -> bool:
        return 0 <= ty < self.tile_height and 0 <= tx < self.tile_width

    def get_tile(self, tx: int, ty: int) -> int:
        if self.in_bounds(tx, ty):
            return int(self.mini_map[ty][tx])
        return 0

    def draw(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0, draw_grid: bool = False):
        if self.tile_width == 0 or self.tile_height == 0:
            return

        start_col = max(0, camera_x // tile_size)
        start_row = max(0, camera_y // tile_size)
        end_col = min(self.tile_width, (camera_x + screen.get_width()) // tile_size + 2)
        end_row = min(self.tile_height, (camera_y + screen.get_height()) // tile_size + 2)

        for ty in range(start_row, end_row):
            row = self.mini_map[ty]
            for tx in range(start_col, end_col):
                tile = row[tx] if tx < len(row) else 0
                tile_id = int(tile) if isinstance(tile, int) else 0
                color = self.tile_colors.get(tile_id, self.tile_colors[0])
                rect = pygame.Rect(tx * tile_size - camera_x, ty * tile_size - camera_y, tile_size, tile_size)
                pygame.draw.rect(screen, color, rect)
                if draw_grid:
                    pygame.draw.rect(screen, (20, 20, 20), rect, 1)

    def is_walkable(self, x: float, y: float) -> bool:

        if x >= tile_size or y >= tile_size:
            tx, ty = int(x // tile_size), int(y // tile_size)
        else:
            tx, ty = int(x), int(y)

        if not self.in_bounds(tx, ty):
            return False
        return self.get_tile(tx, ty) != 1

    def set_tile(self, tx: int, ty: int, tile_id: int):
        if self.in_bounds(tx, ty):
            self.mini_map[ty][tx] = tile_id
