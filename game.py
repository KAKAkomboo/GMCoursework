import pygame
from entities.player import Player
from levels.location_01 import Map
from Settings import screen_width, screen_height, tile_size
class Game:
    def __init__(self, screen, mini_map):
        self.screen = screen
        self.map = Map(mini_map)
        self.player = Player(1, 1, self.map)
        self.camera_x = 0
        self.camera_y = 0
    def update_camera(self):

        self.camera_x = self.player.x * tile_size - screen_width // 2
        self.camera_y = self.player.y * tile_size - screen_height // 2

        self.camera_x = max(0, min(self.camera_x, self.map.width - screen_width))
        self.camera_y = max(0, min(self.camera_y, self.map.height - screen_height))
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
        return None
    def update(self, keys):
        self.player.update(keys)
        self.update_camera()
    def draw(self):
        self.screen.fill((0, 0, 0))
        self.map.draw(self.screen, self.camera_x, self.camera_y)
        self.player.draw(self.screen, self.camera_x, self.camera_y)