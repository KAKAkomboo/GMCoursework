import pygame
import random
import math
from entities.player import Player
from entities.enemies.base_enemy import BaseEnemy
from entities.enemies.shoggoth import Shoggoth
from entities.enemies.deep_one import DeepOne
from entities.enemies.men_of_leng import ManOfLeng
from entities.enemies.ghast import Ghast
from entities.enemies.hound_of_tindalos import HoundOfTindalos
from entities.enemies.nameless_city_dweller import NamelessCityDweller
from entities.enemies.night_gaunt import NightGaunt
from entities.enemies.shantak import Shantak
from entities.friendly_npc import NPC
from entities.base_npc import FriendlyNPC
from world.level_manager import Map
from src.core.settings import tile_size, ENEMIES_ENABLED


class BloodParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = random.randint(2, 6)
        self.color = (random.randint(150, 255), 0, 0)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(20, 50)
        self.gravity = 0.2

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.size = max(0, self.size - 0.05)

    def draw(self, screen, cam_x, cam_y):
        if self.life > 0 and self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x - cam_x), int(self.y - cam_y)), int(self.size))


class Game:
    def __init__(self, screen, mini_map):
        self.screen = screen
        self.mini_map = mini_map
        self.map = Map(mini_map)

        player_start_x = 20
        player_start_y = 30
        self.player = Player(player_start_x, player_start_y, self.map)
        self.player.game_instance = self

        self.camera_x = 0
        self.camera_y = 0

        self.time_scale = 1.0
        self.hit_stop_timer = 0

        self.shake_timer = 0
        self.shake_strength = 0
        self.shake_offset_x = 0
        self.shake_offset_y = 0

        self.blood_particles = []

        self.dialogue_box = None
        self.quest_system = None
        self.notification = None
        self.task_panel = None

        self.enemies = pygame.sprite.Group()
        self.spawn_enemies()

        self.friendly_npcs = []
        villager = FriendlyNPC(self, name="Villager", pos=(18, 20), scale=1.0)
        elder = FriendlyNPC(self, name="Elder", pos=(22, 15), scale=1.0)
        self.friendly_npcs.append(villager)
        self.friendly_npcs.append(elder)

    def spawn_enemies(self):
        if not ENEMIES_ENABLED:
            return

        self.enemies.add(DeepOne(self, (18, 28)))
        self.enemies.add(DeepOne(self, (22, 32)))

        self.enemies.add(ManOfLeng(self, (15, 15)))
        self.enemies.add(ManOfLeng(self, (25, 18)))
        self.enemies.add(Ghast(self, (30, 10)))

        self.enemies.add(Shoggoth(self, (10, 5)))
        self.enemies.add(HoundOfTindalos(self, (35, 5)))
        self.enemies.add(NightGaunt(self, (20, 2)))
        self.enemies.add(Shantak(self, (5, 5)))
        self.enemies.add(NamelessCityDweller(self, (30, 2)))

    def set_dialogue_system(self, db):
        self.dialogue_box = db

    def start_dialogue(self, name, tree, callback):
        if self.dialogue_box:
            self.dialogue_box.start(name, tree, callback)

    def trigger_hit_stop(self, duration_ms, scale=0.05):
        self.hit_stop_timer = duration_ms
        self.time_scale = scale

    def trigger_screen_shake(self, duration_ms, strength):
        self.shake_timer = duration_ms
        self.shake_strength = strength

    def spawn_blood(self, x, y, count=10):
        for _ in range(count):
            self.blood_particles.append(BloodParticle(x, y))

    def update_juice(self, real_dt):
        if self.hit_stop_timer > 0:
            self.hit_stop_timer -= real_dt
            if self.hit_stop_timer <= 0:
                self.time_scale = 1.0
        else:
            self.time_scale = 1.0

        if self.shake_timer > 0:
            self.shake_timer -= real_dt
            self.shake_offset_x = random.uniform(-self.shake_strength, self.shake_strength)
            self.shake_offset_y = random.uniform(-self.shake_strength, self.shake_strength)
        else:
            self.shake_offset_x = 0
            self.shake_offset_y = 0

        for bp in self.blood_particles[:]:
            bp.update()
            if bp.life <= 0:
                self.blood_particles.remove(bp)

    def update_camera(self):
        screen_w, screen_h = self.screen.get_size()

        target_x = int(self.player.x * tile_size - screen_w // 2)
        target_y = int(self.player.y * tile_size - screen_h // 2)

        map_pixel_w = getattr(self.map, "width", None)
        map_pixel_h = getattr(self.map, "height", None)

        if map_pixel_w is not None and map_pixel_h is not None:
            target_x = max(0, min(target_x, map_pixel_w - screen_w))
            target_y = max(0, min(target_y, map_pixel_h - screen_h))

        self.camera_x = target_x + self.shake_offset_x
        self.camera_y = target_y + self.shake_offset_y

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_p:
                    return "pause"
        return None

    def update(self, keys, mouse_clicked=False, shoot=False, shoot_dir_right=True, lock_pressed=False):
        raw_dt = 16.0
        self.update_juice(raw_dt)
        game_dt = raw_dt * self.time_scale

        self.player.update(keys, npc_group=self.enemies, mouse_clicked=mouse_clicked, dt=game_dt)
        self.enemies.update(dt=game_dt)

        for fnpc in self.friendly_npcs:
            fnpc.update()

        self.update_camera()

    def draw(self):
        self.screen.fill((30, 30, 30))

        cam_x_int = int(self.camera_x)
        cam_y_int = int(self.camera_y)

        self.map.draw(self.screen, cam_x_int, cam_y_int)

        for enemy in self.enemies:
            enemy.draw(self.screen, cam_x_int, cam_y_int)

        for fnpc in self.friendly_npcs:
            fnpc.draw(self.screen, cam_x_int, cam_y_int)

        self.player.draw(self.screen, cam_x_int, cam_y_int)

        for bp in self.blood_particles:
            bp.draw(self.screen, cam_x_int, cam_y_int)

    def respawn_enemies(self):
        self.enemies.empty()
        if ENEMIES_ENABLED:
            self.spawn_enemies()
