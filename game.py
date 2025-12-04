import pygame
from entities.player import Player
from levels.location_01 import Map
from Settings import screen_width, screen_height, tile_size
from entities.NPC import NPC


class Game:
    def __init__(self, screen, mini_map):
        self.screen = screen
        self.mini_map = mini_map  # Store mini_map for NPC access
        self.map = Map(mini_map)
        self.player = Player(1, 1, self.map)
        self.camera_x = 0
        self.camera_y = 0

        self.npc_group = pygame.sprite.Group()

        npc1 = NPC(self, pos=(10.5, 5.5), path='', scale=1.0, animation_time=180)
        self.npc_group.add(npc1)

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
                if event.key == pygame.K_e:
                    for npc in self.npc_group:
                        if self.player_rect().colliderect(npc.rect):
                            npc.interact()
        return None

    def player_rect(self):
        return pygame.Rect(
            self.player.x * tile_size,
            self.player.y * tile_size,
            self.player.image.get_width(),
            self.player.image.get_height()
        )

    def update(self, keys):
        dt = pygame.time.get_ticks() / 1000
        self.player.update(keys)
        self.npc_group.update(dt)
        self.update_camera()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.map.draw(self.screen, self.camera_x, self.camera_y)

        for npc in self.npc_group:
            offset_rect = npc.rect.move(-self.camera_x, -self.camera_y)
            self.screen.blit(npc.image, offset_rect)

        self.player.draw(self.screen, self.camera_x, self.camera_y)