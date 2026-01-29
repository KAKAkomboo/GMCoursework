import pygame
import math
import random
from .base_enemy import BaseEnemy

class Ghast(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (80, 80), 250, 0.02)
        self.image.fill((100, 80, 80))
        
        self.attack_range = 2.5
        self.attack_cooldown = 4000
        self.last_attack = 0
        
        self.stomp_radius = 3.0

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "ATTACK"]:
            return

        if player_dist < self.attack_range and now - self.last_attack > self.attack_cooldown:
            if random.random() > 0.4:
                self.start_attack()
            else:
                self.start_stomp()
        elif player_dist < self.vision_range:
            self.state = "CHASE"
            self.chase_player(dt)
        else:
            self.state = "IDLE"

    def start_attack(self):
        self.state = "ATTACK"
        self.last_attack = pygame.time.get_ticks()
        self.state_timer = 1200
        self.attack_phase = "STARTUP"

    def start_stomp(self):
        self.state = "ATTACK"
        self.last_attack = pygame.time.get_ticks()
        self.state_timer = 1500
        self.attack_phase = "STOMP_STARTUP"

    def update(self, dt):
        super().update(dt)
        if self.state == "ATTACK":
            self.update_attack(dt)

    def update_attack(self, dt):
        elapsed = self.state_timer
        
        if self.attack_phase == "STOMP_STARTUP":
            if elapsed < 1000:
                pass
            else:
                player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
                player_dist = self.pos.distance_to(player_pos)
                if player_dist < self.stomp_radius:
                    self.game.player.take_damage(25)
                    if hasattr(self.game.player, "trigger_stagger"):
                        self.game.player.trigger_stagger(500)
                
                if self.game.game_instance:
                    self.game.game_instance.trigger_screen_shake(300, 10)
                
                self.attack_phase = "RECOVERY"
        
        elif self.attack_phase == "STARTUP":
            if elapsed < 800:
                pass
            else:
                self.attack_phase = "ACTIVE"
                player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
                player_dist = self.pos.distance_to(player_pos)
                if player_dist < self.attack_range:
                    self.game.player.take_damage(40)
                
                self.attack_phase = "RECOVERY"
