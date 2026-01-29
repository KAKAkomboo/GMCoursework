import pygame
import math
import random
from .base_enemy import BaseEnemy

class ManOfLeng(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (32, 48), 70, 0.1)
        self.image.fill((150, 120, 100))
        
        self.attack_range = 1.0
        self.attack_cooldown = 1800
        self.last_attack = 0
        
        self.is_stealthed = False
        self.stealth_timer = 0
        self.stealth_duration = 3000
        
        self.poison_damage = 2
        self.poison_duration = 5000

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "ATTACK"]:
            return

        if not self.is_stealthed and player_dist > 5:
            self.is_stealthed = True
            self.image.set_alpha(100)
        elif self.is_stealthed and player_dist <= 2:
            self.is_stealthed = False
            self.image.set_alpha(255)

        if player_dist < 1.5 and self.is_behind_player():
            self.start_attack(is_backstab=True)
            return

        if player_dist < self.attack_range and now - self.last_attack > self.attack_cooldown:
            self.start_attack()
        elif player_dist < self.vision_range:
            self.state = "CHASE"
            self.chase_player(dt)
        else:
            self.state = "IDLE"

    def start_attack(self, is_backstab=False):
        self.state = "ATTACK"
        self.last_attack = pygame.time.get_ticks()
        self.state_timer = 500
        
        if is_backstab:
            self.game.player.take_damage(30)
        else:
            self.game.player.take_damage(10)

    def is_behind_player(self):
        player_angle = self.game.player.facing_angle
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        to_player_angle = math.degrees(math.atan2(self.pos.y - player_pos.y, self.pos.x - player_pos.x))
        
        angle_diff = (player_angle - to_player_angle + 180) % 360 - 180
        return abs(angle_diff) < 45
