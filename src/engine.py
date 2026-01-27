import pygame
from entities.player import Player
from entities.friendly_npc import NPC
from entities.base_npc import FriendlyNPC
from world.level_manager import Map
from src.core.settings import tile_size

class Game:
    def __init__(self, screen, mini_map):
        self.screen = screen
        self.mini_map = mini_map
        self.map = Map(mini_map)

        self.player = Player(1, 1, self.map)
        self.camera_x = 0
        self.camera_y = 0

        self.npc_group = pygame.sprite.Group()
        self.initial_npc_positions = []

        npc1 = NPC(self, pos=(5.5, 4.5), scale=1.0, animation_time=180)
        npc2 = NPC(self, pos=(8.5, 6.5), scale=1.0, animation_time=180)
        self.npc_group.add(npc1, npc2)
        self.initial_npc_positions.append((5.5, 4.5))
        self.initial_npc_positions.append((8.5, 6.5))

        self.friendly_npcs = []
        villager = FriendlyNPC(self, name="Villager", pos=(12.5, 6.5), scale=1.0)
        elder = FriendlyNPC(self, name="Elder", pos=(15.5, 8.5), scale=1.0)
        self.friendly_npcs.append(villager)
        self.friendly_npcs.append(elder)

    def update_camera(self):
        screen_w, screen_h = self.screen.get_size()
        
        self.camera_x = int(self.player.x * tile_size - screen_w // 2)
        self.camera_y = int(self.player.y * tile_size - screen_h // 2)

        map_pixel_w = getattr(self.map, "width", None)
        map_pixel_h = getattr(self.map, "height", None)
        if map_pixel_w is None or map_pixel_h is None:
            return

        self.camera_x = max(0, min(self.camera_x, map_pixel_w - screen_w))
        self.camera_y = max(0, min(self.camera_y, map_pixel_h - screen_h))

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_p:
                    return "pause"
        return None

    def update(self, keys, mouse_clicked=False, shoot=False, shoot_dir_right=True, lock_pressed=False):
        npc_list = list(self.npc_group)
        self.player.update(keys, npc_group=npc_list, mouse_clicked=mouse_clicked, dt=1.0,
                           shoot=shoot, shoot_dir_right=shoot_dir_right, lock_pressed=lock_pressed)

        for npc in list(self.npc_group):
            npc.update()
            if not npc.alive:
                pass

        for fnpc in self.friendly_npcs:
            fnpc.update()

        self.update_camera()

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.map.draw(self.screen, self.camera_x, self.camera_y)

        for npc in self.npc_group:
            offset_rect = npc.rect.move(-self.camera_x, -self.camera_y)
            self.screen.blit(npc.image, offset_rect)
            npc.draw_health_bar(self.screen, self.camera_x, self.camera_y)

        for fnpc in self.friendly_npcs:
            fnpc.draw(self.screen, self.camera_x, self.camera_y)

        self.player.draw(self.screen, self.camera_x, self.camera_y)

    def respawn_enemies(self):
        npc_list = list(self.npc_group)
        for i, npc in enumerate(npc_list):
            if i < len(self.initial_npc_positions):
                pos = self.initial_npc_positions[i]
                npc.pos = (float(pos[0]), float(pos[1]))
                npc.rect.center = (int(npc.pos[0] * tile_size), int(npc.pos[1] * tile_size))
                npc.health = getattr(npc, "max_health", npc.health)
                npc.alive = True
                npc.state = 'idle'
                npc.path = []
                npc.path_index = 0
