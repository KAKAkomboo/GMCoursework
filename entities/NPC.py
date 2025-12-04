import math
import pygame
from random import randint, choice
from collections import deque  # For BFS queue

from Settings import tile_size

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, pos=(10.5, 5.5), path='', scale=1.0, animation_time=180):
        super().__init__()
        self.game = game
        self.pos = pos
        self.scale = scale
        self.animation_time = animation_time

        size = (int(tile_size * scale), int(tile_size * scale))
        self.idle_image = [pygame.Surface(size).convert_alpha()]
        self.walk_image = [pygame.Surface(size).convert_alpha()]
        self.attack_image = [pygame.Surface(size).convert_alpha()]
        self.death_image = [pygame.Surface(size).convert_alpha()]

        pygame.draw.rect(self.idle_image[0], (0, 255, 0), self.idle_image[0].get_rect())
        pygame.draw.rect(self.walk_image[0], (0, 0, 255), self.walk_image[0].get_rect())
        pygame.draw.rect(self.attack_image[0], (255, 0, 0), self.attack_image[0].get_rect())
        pygame.draw.rect(self.death_image[0], (0, 0, 0), self.death_image[0].get_rect())

        self.image = self.idle_image[0]
        self.rect = self.image.get_rect(center=(self.pos[0] * tile_size, self.pos[1] * tile_size))

        self.health = 100
        self.max_health = 100
        self.speed = 0.1
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

    def update(self, dt=None):
        if self.alive:
            self.run_logic()
            self.animate()
            self.rect.center = (self.pos[0] * tile_size, self.pos[1] * tile_size)
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
            dist = math.sqrt(dx ** 2 + dy ** 2)

            if dist <= self.speed:
                self.pos = (next_pos[0], next_pos[1])
                self.path_index += 1
            else:
                self.pos = (
                    self.pos[0] + (dx / dist) * self.speed,
                    self.pos[1] + (dy / dist) * self.speed
                )

    def attack(self):
        if self.animation_trigger:
            self.game.player.take_damage(self.attack_damage)

    def check_wall(self, x, y):
        tile_x, tile_y = int(x), int(y)
        if 0 <= tile_y < len(self.game.mini_map) and 0 <= tile_x < len(self.game.mini_map[0]):
            return self.game.mini_map[tile_y][tile_x] == 0
        return False

    def find_path(self, start, goal):
        queue = deque([start])
        came_from = {start: None}
        visited = set([start])

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            current = queue.popleft()
            if current == goal:
                break

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if (neighbor not in visited and
                    0 <= neighbor[1] < len(self.game.mini_map) and
                    0 <= neighbor[0] < len(self.game.mini_map[0]) and
                    self.game.mini_map[neighbor[1]][neighbor[0]] == 0):
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
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.state = 'death'

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
        print("Interacting with NPC!")

    def draw(self, screen):
        screen.blit(self.image, self.rect)