import pygame
import math
import random
from .base_enemy import BaseEnemy

class Shantak(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (128, 128), 500, 0.06)
        self.image.fill((120, 100, 80))
        self.is_flying = True
        self.altitude = 100
        
        self.dive_cooldown = 8000
        self.last_dive = 0

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "DIVING"]:
            return

        if player_dist < 10 and now - self.last_dive > self.dive_cooldown:
            self.start_dive()
        else:
            self.chase_player(dt)

    def start_dive(self):
        self.state = "DIVING"
        self.state_timer = 2000
        self.last_dive = pygame.time.get_ticks()
        self.dive_target = pygame.math.Vector2(self.game.player.x, self.game.player.y)

    def update(self, dt):
        super().update(dt)
        if self.state == "DIVING":
            self.update_dive(dt)

    def update_dive(self, dt):
        direction = (self.dive_target - self.pos).normalize()
        self.pos += direction * self.speed * 3 * (dt / 16.0)
        
        progress = 1 - (self.state_timer / 2000)
        self.altitude = 100 * (1 - math.sin(progress * math.pi))
        
        if self.state_timer <= 0:
            self.state = "IDLE"
            self.altitude = 100

    def draw(self, screen, cam_x, cam_y):
        shadow_size = 15 + (1 - self.altitude/100) * 30
        shadow_pos = (self.pos.x - cam_x, self.pos.y - cam_y)
        pygame.draw.circle(screen, (0, 0, 0, 100), shadow_pos, int(shadow_size))
        
        draw_pos = (self.pos.x - cam_x, self.pos.y - cam_y - self.altitude)
        screen.blit(self.image, self.rect.move(draw_pos))
