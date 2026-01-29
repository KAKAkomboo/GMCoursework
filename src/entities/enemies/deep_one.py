import pygame
import math
import random
from .base_enemy import BaseEnemy

class DeepOne(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (32, 48), 80, 0.08)
        self.image.fill((0, 100, 120))
        
        self.attack_range = 1.2
        self.leap_range = 7.0
        self.attack_cooldown = 1500
        self.last_attack = 0
        
        self.is_enraged = False
        self.combo_count = 0
        self.max_combo = 3

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "ATTACK", "LEAP"]:
            return

        if self.health < self.max_health * 0.4 and not self.is_enraged:
            self.is_enraged = True
            self.speed *= 1.5
            self.attack_cooldown *= 0.5
            self.image.fill((100, 150, 180))

        if player_dist < self.attack_range:
            if now - self.last_attack > self.attack_cooldown:
                self.start_attack()
        elif player_dist < self.leap_range and self.rally_timer > 0:
            self.start_leap()
        elif player_dist < self.vision_range:
            self.state = "CHASE"
            self.chase_player(dt)
        else:
            self.state = "IDLE"

    def start_attack(self):
        self.state = "ATTACK"
        self.last_attack = pygame.time.get_ticks()
        self.combo_count = 0
        self.attack_timer = 0
        self.attack_phase = "STARTUP"

    def start_leap(self):
        self.state = "LEAP"
        self.state_timer = 800
        self.leap_target = pygame.math.Vector2(self.game.player.x, self.game.player.y)

    def update(self, dt):
        super().update(dt)
        
        if self.state == "ATTACK":
            self.update_attack(dt)
        elif self.state == "LEAP":
            self.update_leap(dt)

    def update_attack(self, dt):
        self.attack_timer += dt
        
        if self.attack_timer > 300:
            self.attack_timer = 0
            self.combo_count += 1
            
            player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
            player_dist = self.pos.distance_to(player_pos)
            if player_dist < self.attack_range:
                self.game.player.take_damage(10)
            
            if self.combo_count >= self.max_combo:
                self.state = "IDLE"

    def update_leap(self, dt):
        direction = (self.leap_target - self.pos).normalize()
        self.pos += direction * self.speed * 2 * (dt / 16.0)
        
        if self.state_timer <= 0:
            self.state = "IDLE"
            self.start_attack()

    def draw(self, screen, cam_x, cam_y):
        super().draw(screen, cam_x, cam_y)
