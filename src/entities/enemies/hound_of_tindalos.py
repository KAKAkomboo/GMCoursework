import pygame
import math
import random
from .base_enemy import BaseEnemy

class HoundOfTindalos(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (40, 40), 60, 0.15)
        self.image.fill((50, 50, 150))
        
        self.teleport_cooldown = 4000
        self.last_teleport = 0
        self.is_visible = True

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "TELEPORTING"]:
            return

        if now - self.last_teleport > self.teleport_cooldown:
            self.start_teleport()
        
        if self.is_visible:
            if player_dist < self.attack_range:
                self.start_attack()
            else:
                self.chase_player(dt)

    def start_teleport(self):
        self.state = "TELEPORTING"
        self.state_timer = 500
        self.is_visible = False
        self.last_teleport = pygame.time.get_ticks()

    def update(self, dt):
        super().update(dt)
        if self.state == "TELEPORTING" and self.state_timer <= 0:
            self.reappear()

    def reappear(self):
        self.state = "IDLE"
        self.is_visible = True
        
        angle = random.uniform(0, 360)
        dist = random.uniform(3, 6)
        rad = math.radians(angle)
        
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        self.pos.x = player_pos.x + math.cos(rad) * dist
        self.pos.y = player_pos.y + math.sin(rad) * dist

    def start_attack(self):
        self.state = "ATTACK"
        self.state_timer = 200
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        self.attack_dir = (player_pos - self.pos).normalize()
        
    def draw(self, screen, cam_x, cam_y):
        if self.is_visible:
            super().draw(screen, cam_x, cam_y)
