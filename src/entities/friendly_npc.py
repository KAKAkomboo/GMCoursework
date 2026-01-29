import math
import pygame
from random import randint, choice
from collections import deque
from src.core.settings import tile_size

class NPC(pygame.sprite.Sprite):
    def __init__(self, game, pos=(10.5, 5.5), scale=1.0, animation_time=180):
        super().__init__()
        self.game = game
        self.pos = [float(pos[0]), float(pos[1])]
        self.scale = float(scale)
        self.animation_time = int(animation_time)

        size = (int(tile_size * self.scale), int(tile_size * self.scale))
        self.idle_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        self.walk_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        self.attack_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        self.stagger_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()] # New
        self.visceral_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()] # New
        self.death_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]

        pygame.draw.rect(self.idle_image[0], (0, 200, 0), self.idle_image[0].get_rect()) # Green
        pygame.draw.rect(self.walk_image[0], (0, 0, 200), self.walk_image[0].get_rect()) # Blue
        pygame.draw.rect(self.attack_image[0], (200, 0, 0), self.attack_image[0].get_rect()) # Red
        pygame.draw.rect(self.stagger_image[0], (200, 200, 0), self.stagger_image[0].get_rect()) # Yellow
        pygame.draw.rect(self.visceral_image[0], (255, 100, 0), self.visceral_image[0].get_rect()) # Orange
        pygame.draw.rect(self.death_image[0], (50, 50, 50), self.death_image[0].get_rect()) # Grey

        self.image = self.idle_image[0]
        self.rect = self.image.get_rect(center=(int(self.pos[0] * tile_size), int(self.pos[1] * tile_size)))

        self.health = 100
        self.max_health = 100
        self.speed = 0.15
        self.attack_damage = 15
        self.attack_range = 1.5
        self.vision_range = 10.0
        self.alive = True
        self.currency_reward = 10000
        self.invincible = False
        self.invincible_timer = 0

        self.state = 'IDLE'
        self.last_state = 'IDLE'
        self.state_timer = 0

        self.attack_startup_time = 500
        self.attack_active_time = 200
        self.attack_recovery_time = 800
        self.attack_cooldown = 2000
        self.last_attack_time = 0
        self.attack_phase = 'NONE'
        self.has_attacked_player = False
        self.attack_target_pos = (0, 0)

        self.chasing_player = False
        self.path = []
        self.path_index = 0
        self.path_update_delay = 500 # ms
        self.last_path_update = 0

    def update(self, dt=16.0):
        if not self.alive:
            self.animate_death()
            return

        self.run_logic(dt)
        self.animate()
        self.rect.center = (int(self.pos[0] * tile_size), int(self.pos[1] * tile_size))

        if self.state_timer > 0:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.reset_state()

        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

    def run_logic(self, dt):
        player_pos = (self.game.player.x, self.game.player.y)
        dist_to_player = math.dist(self.pos, player_pos)
        now = pygame.time.get_ticks()

        if self.state in ['STAGGERED', 'OPEN_FOR_VISCERAL', 'ATTACK']:
            self.handle_combat_state(dt)
            return

        if dist_to_player <= self.vision_range:
            self.chasing_player = True
            if dist_to_player <= self.attack_range:
                if now - self.last_attack_time > self.attack_cooldown:
                    self.state = 'ATTACK'
                    self.start_attack()
            else:
                self.state = 'CHASE'
                self.move_towards_player(now, dt)
        else:
            self.chasing_player = False
            self.state = 'IDLE'


    def handle_combat_state(self, dt):
        if self.state == 'ATTACK':
            self.update_attack_phase(dt)
        elif self.state == 'STAGGERED':
            pass
        elif self.state == 'OPEN_FOR_VISCERAL':
            pass

    def start_attack(self):
        self.attack_phase = 'STARTUP'
        self.state_timer = self.attack_startup_time + self.attack_active_time + self.attack_recovery_time
        self.last_attack_time = pygame.time.get_ticks()
        self.has_attacked_player = False
        self.attack_target_pos = (self.game.player.x, self.game.player.y)

    def update_attack_phase(self, dt):
        
        total_duration = self.attack_startup_time + self.attack_active_time + self.attack_recovery_time
        elapsed = total_duration - self.state_timer
        
        if elapsed < self.attack_startup_time:
            self.attack_phase = 'STARTUP'
            dx = self.attack_target_pos[0] - self.pos[0]
            dy = self.attack_target_pos[1] - self.pos[1]
            self.facing_angle = math.degrees(math.atan2(dy, dx))
        elif elapsed < self.attack_startup_time + self.attack_active_time:
            self.attack_phase = 'ACTIVE'
            if not self.has_attacked_player:
                self.check_player_hit()
                self.has_attacked_player = True
        elif elapsed < total_duration:
            self.attack_phase = 'RECOVERY'
        else:
            self.state = 'IDLE'
            self.attack_phase = 'NONE'

    def check_player_hit(self):
        player_pos = (self.game.player.x, self.game.player.y)
        dist_to_player = math.dist(self.pos, player_pos)
        if dist_to_player <= self.attack_range:
            self.game.player.take_damage(self.attack_damage)
            if self.game: 
                self.game.trigger_hit_stop(70)
                self.game.trigger_screen_shake(150, 5)

    def check_parry_window(self):
        return self.state == 'ATTACK' and self.attack_phase == 'STARTUP'

    def trigger_stagger(self, duration_ms):
        self.state = 'STAGGERED'
        self.state_timer = duration_ms
        self.invincible = True
        self.invincible_timer = duration_ms

    def trigger_open_for_visceral(self):
        self.state = 'OPEN_FOR_VISCERAL'
        self.state_timer = 2000
        self.invincible = True
        self.invincible_timer = 2000

    def reset_state(self):
        self.state = 'IDLE'
        self.state_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.attack_phase = 'NONE'
        self.has_attacked_player = False

    def move_towards_player(self, now, dt):
        if now - self.last_path_update > self.path_update_delay:
            player_tile = (int(self.game.player.x), int(self.game.player.y))
            npc_tile = (int(self.pos[0]), int(self.pos[1]))
            self.path = self.find_path(npc_tile, player_tile)
            self.path_index = 0
            self.last_path_update = now

        move_step = self.speed * (dt / 16.0)

        if self.path and self.path_index < len(self.path):
            next_tile_center = (self.path[self.path_index][0] + 0.5, self.path[self.path_index][1] + 0.5)
            
            dx = next_tile_center[0] - self.pos[0]
            dy = next_tile_center[1] - self.pos[1]
            dist = math.hypot(dx, dy)
            
            if dist < move_step * 2:
                self.pos[0] = next_tile_center[0]
                self.pos[1] = next_tile_center[1]
                self.path_index += 1
            else:
                self.pos[0] += (dx / dist) * move_step
                self.pos[1] += (dy / dist) * move_step
        else:
            dx = self.game.player.x - self.pos[0]
            dy = self.game.player.y - self.pos[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.pos[0] += (dx / dist) * move_step
                self.pos[1] += (dy / dist) * move_step

    def check_wall(self, x, y):
        tile_x, tile_y = int(x), int(y)
        if 0 <= tile_y < len(self.game.mini_map) and 0 <= tile_x < len(self.game.mini_map[0]):
            return self.game.mini_map[tile_y][tile_x] == 0
        return False

    def find_path(self, start, goal):
        if start == goal: return []
        queue = deque([start])
        came_from = {start: None}
        visited = set([start])
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            current = queue.popleft()
            if current == goal: break
            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if (0 <= neighbor[1] < len(self.game.mini_map) and
                        0 <= neighbor[0] < len(self.game.mini_map[0]) and
                        self.game.mini_map[neighbor[1]][neighbor[0]] == 0):
                    if neighbor not in visited:
                        queue.append(neighbor)
                        visited.add(neighbor)
                        came_from[neighbor] = current

        if goal not in came_from: return []
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path[1:]

    def take_damage(self, damage):
        if not self.alive or self.invincible: return
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.state = 'DEATH'
            if hasattr(self.game, "player") and hasattr(self.game.player, "add_currency"):
                self.game.player.add_currency(self.currency_reward)
        else:
            self.trigger_stagger(200)
            if self.game:
                self.game.spawn_blood(self.rect.centerx, self.rect.centery, 5)

    def animate(self):
        if self.state == 'IDLE':
            self.image = self.idle_image[0]
        elif self.state == 'CHASE':
            self.image = self.walk_image[0]
        elif self.state == 'ATTACK':
            self.image = self.attack_image[0]
        elif self.state == 'STAGGERED':
            self.image = self.stagger_image[0]
        elif self.state == 'OPEN_FOR_VISCERAL':
            self.image = self.visceral_image[0]
        elif self.state == 'DEATH':
            self.image = self.death_image[0]

    def animate_death(self):
        self.image = self.death_image[0]

    def interact(self):
        print("Interacting with NPC")

    def draw_health_bar(self, screen, camera_x, camera_y):
        if not self.alive: return
        bar_width = int(tile_size * self.scale * 0.8)
        bar_height = max(4, int(tile_size * 0.08))
        screen_x = int(self.pos[0] * tile_size - camera_x)
        screen_y = int(self.pos[1] * tile_size - camera_y)

        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - int(tile_size * self.scale * 0.75) - bar_height

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = max(0.0, min(1.0, self.health / self.max_health))
        current_width = int(bar_width * health_ratio)
        if health_ratio > 0.6: color = (0, 255, 0)
        elif health_ratio > 0.3: color = (255, 255, 0)
        else: color = (255, 0, 0)
        if current_width > 0:
            pygame.draw.rect(screen, color, (bar_x, bar_y, current_width, bar_height))

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.pos[0] * tile_size - camera_x - (self.rect.width / 2)
        screen_y = self.pos[1] * tile_size - camera_y - (self.rect.height / 2)
        screen.blit(self.image, (screen_x, screen_y))
        self.draw_health_bar(screen, camera_x, camera_y)
