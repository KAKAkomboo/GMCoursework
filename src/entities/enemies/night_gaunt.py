import pygame
import math
import random
from .base_enemy import BaseEnemy

class NightGaunt(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (50, 50), 90, 0.07)
        self.image.fill((30, 30, 40))
        self.is_flying = True
        self.altitude = 50
        
        self.grab_cooldown = 6000
        self.last_grab = 0

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "GRABBING"]:
            return

        if player_dist < 2.0 and now - self.last_grab > self.grab_cooldown:
            self.start_grab()
        else:
            self.chase_player(dt)

    def start_grab(self):
        self.state = "GRABBING"
        self.state_timer = 1500
        self.last_grab = pygame.time.get_ticks()

    def update(self, dt):
        super().update(dt)
        if self.state == "GRABBING" and self.state_timer <= 0:
            self.state = "IDLE"

    def chase_player(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        target_pos = player_pos + pygame.math.Vector2(0, -self.altitude / 10)
        direction = (target_pos - self.pos).normalize()
        self.pos += direction * self.speed * (dt / 16.0)

    def draw(self, screen, cam_x, cam_y):
        shadow_pos = (self.pos.x - cam_x, self.pos.y - cam_y)
        pygame.draw.circle(screen, (0, 0, 0, 100), shadow_pos, 15)

        draw_pos = (self.pos.x - cam_x, self.pos.y - cam_y - self.altitude)
        screen.blit(self.image, self.rect.move(draw_pos))
