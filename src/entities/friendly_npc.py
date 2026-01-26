import math
import pygame
from random import randint, choice
from collections import deque
from src.core.settings import tile_size

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, pos=(10.5, 5.5), scale=1.0, animation_time=180):
        super().__init__()
        self.game = game
        self.pos = (float(pos[0]), float(pos[1]))
        self.scale = float(scale)
        self.animation_time = int(animation_time)

        size = (int(tile_size * self.scale), int(tile_size * self.scale))
        self.idle_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        self.walk_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        self.attack_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        self.death_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]

        pygame.draw.rect(self.idle_image[0], (0, 200, 0), self.idle_image[0].get_rect())
        pygame.draw.rect(self.walk_image[0], (0, 0, 200), self.walk_image[0].get_rect())
        pygame.draw.rect(self.attack_image[0], (200, 0, 0), self.attack_image[0].get_rect())
        pygame.draw.rect(self.death_image[0], (50, 50, 50), self.death_image[0].get_rect())

        self.image = self.idle_image[0]
        self.rect = self.image.get_rect(center=(int(self.pos[0] * tile_size), int(self.pos[1] * tile_size)))

        self.health = 100
        self.max_health = 100
        self.speed = 0.2
        self.attack_damage = 10
        self.attack_range = 1.0
        self.vision_range = 20.0
        self.alive = True
        self.state = 'idle'
        self.frame_counter = 0
        self.animation_trigger = False
        self.last_update = pygame.time.get_ticks()

        self.chasing_player = False
        self.path = []
        self.path_index = 0

        self.currency_reward = 10

    def update(self, dt=None):
        if self.alive:
            self.run_logic()
            self.animate()
            self.rect.center = (int(self.pos[0] * tile_size), int(self.pos[1] * tile_size))
        else:
            self.animate_death()

    def run_logic(self):
        player_pos = (self.game.player.x, self.game.player.y)
        dist_to_player = math.dist(self.pos, player_pos)

        if dist_to_player <= self.vision_range:
            self.chasing_player = True
            if dist_to_player <= self.attack_range:
                self.state = 'attack'
                self.attack()
                self.path = []
                self.path_index = 0
            else:
                self.state = 'walk'
                self.move_towards_player()
        else:
            self.chasing_player = False
            self.state = 'idle'
            if randint(0, 100) < 5:
                self.random_move()

    def move_towards_player(self):
        player_tile = (int(self.game.player.x), int(self.game.player.y))
        npc_tile = (int(self.pos[0]), int(self.pos[1]))

        if not self.path or self.path_index >= len(self.path) or self.path[-1] != player_tile:
            self.path = self.find_path(npc_tile, player_tile)
            self.path_index = 0

        if self.path and self.path_index < len(self.path):
            next_pos = self.path[self.path_index]
            dx = next_pos[0] - self.pos[0]
            dy = next_pos[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist <= self.speed:
                self.pos = (next_pos[0], next_pos[1])
                self.path_index += 1
            else:
                self.pos = (self.pos[0] + (dx / dist) * self.speed, self.pos[1] + (dy / dist) * self.speed)

    def attack(self):
        if self.animation_trigger:
            self.game.player.take_damage(self.attack_damage)

    def check_wall(self, x, y):
        tile_x, tile_y = int(x), int(y)
        if 0 <= tile_y < len(self.game.mini_map) and 0 <= tile_x < len(self.game.mini_map[0]):
            return self.game.mini_map[tile_y][tile_x] == 0
        return False

    def find_path(self, start, goal):
        if start == goal:
            return []
        queue = deque([start])
        came_from = {start: None}
        visited = set([start])

        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]

        while queue:
            current = queue.popleft()
            if current == goal:
                break
            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[1] < len(self.game.mini_map) and
                        0 <= neighbor[0] < len(self.game.mini_map[0]) and
                        self.game.mini_map[neighbor[1]][neighbor[0]] == 0):
                    if abs(dx) == 1 and abs(dy) == 1:
                        adj1 = (current[0] + dx, current[1])
                        adj2 = (current[0], current[1] + dy)
                        if not (self.game.mini_map[adj1[1]][adj1[0]] == 0 and
                                self.game.mini_map[adj2[1]][adj2[0]] == 0):
                            continue
                    if neighbor not in visited:
                        queue.append(neighbor)
                        visited.add(neighbor)
                        came_from[neighbor] = current

        if goal not in came_from:
            return []

        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path[1:]

    def take_damage(self, damage):
        if not self.alive:
            return
        self.health -= damage
        print(f"NPC at {self.pos} took {damage} damage. Remaining {self.health}")
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.state = 'death'
            if hasattr(self.game, "player") and hasattr(self.game.player, "add_currency"):
                self.game.player.add_currency(self.currency_reward)

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_time:
            self.last_update = now
            self.animation_trigger = True
            if self.state == 'idle':
                self.frame_counter = (self.frame_counter + 1) % len(self.idle_image)
                self.image = self.idle_image[self.frame_counter]
            elif self.state == 'walk':
                self.frame_counter = (self.frame_counter + 1) % len(self.walk_image)
                self.image = self.walk_image[self.frame_counter]
            elif self.state == 'attack':
                self.frame_counter = (self.frame_counter + 1) % len(self.attack_image)
                self.image = self.attack_image[self.frame_counter]
        else:
            self.animation_trigger = False

    def animate_death(self):
        self.image = self.death_image[0]

    def random_move(self):
        npc_tile = (int(self.pos[0]), int(self.pos[1]))
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        possible_goals = []
        for dx, dy in directions:
            goal = (npc_tile[0] + dx * 2, npc_tile[1] + dy * 2)
            if (0 <= goal[1] < len(self.game.mini_map) and
                    0 <= goal[0] < len(self.game.mini_map[0]) and
                    self.game.mini_map[goal[1]][goal[0]] == 0):
                possible_goals.append(goal)
        if possible_goals:
            goal = choice(possible_goals)
            self.path = self.find_path(npc_tile, goal)
            self.path_index = 0
            self.state = 'walk'

    def interact(self):
        print("Interacting with NPC")

    def draw_health_bar(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        bar_width = int(tile_size * self.scale * 0.8)
        bar_height = max(4, int(tile_size * 0.08))
        screen_x = int(self.pos[0] * tile_size - camera_x)
        screen_y = int(self.pos[1] * tile_size - camera_y)

        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - int(tile_size * self.scale * 0.75) - bar_height

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = max(0.0, min(1.0, self.health / self.max_health))
        current_width = int(bar_width * health_ratio)
        if health_ratio > 0.6:
            color = (0, 255, 0)
        elif health_ratio > 0.3:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        if current_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, current_width, bar_height))

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.pos[0] * tile_size - camera_x - (self.rect.width / 2)
        screen_y = self.pos[1] * tile_size - camera_y - (self.rect.height / 2)
        screen.blit(self.image, (screen_x, screen_y))
        self.draw_health_bar(screen, camera_x, camera_y)
