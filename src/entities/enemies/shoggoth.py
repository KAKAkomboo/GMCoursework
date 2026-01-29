import pygame
import math
import random
from .base_enemy import BaseEnemy

class Shoggoth(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (64, 64), 200, 0.03)
        self.image.fill((50, 100, 50))
        
        self.attack_range = 3.0
        self.attack_cooldown = 2500
        self.last_attack = 0
        
        self.tentacles = []

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "ATTACK"]:
            return

        if player_dist < self.attack_range and now - self.last_attack > self.attack_cooldown:
            self.start_attack()
        elif player_dist < self.vision_range:
            self.state = "CHASE"
            self.chase_player(dt)
        else:
            self.state = "IDLE"

    def start_attack(self):
        self.state = "ATTACK"
        self.last_attack = pygame.time.get_ticks()
        
        self.tentacles = []
        for _ in range(random.randint(3, 6)):
            angle = random.uniform(0, 360)
            length = random.uniform(50, 120)
            duration = random.uniform(500, 1000)
            self.tentacles.append({"angle": angle, "length": length, "timer": duration, "max_timer": duration})

    def update(self, dt):
        super().update(dt)
        
        if self.state == "ATTACK":
            for tentacle in self.tentacles[:]:
                tentacle["timer"] -= dt
                if tentacle["timer"] <= 0:
                    self.tentacles.remove(tentacle)
            
            if not self.tentacles:
                self.state = "IDLE"

    def draw(self, screen, cam_x, cam_y):
        super().draw(screen, cam_x, cam_y)
        
        if self.state == "ATTACK":
            for tentacle in self.tentacles:
                progress = tentacle["timer"] / tentacle["max_timer"]
                current_len = tentacle["length"] * math.sin(progress * math.pi)
                
                rad = math.radians(tentacle["angle"])
                end_pos = (
                    self.pos.x + math.cos(rad) * current_len,
                    self.pos.y + math.sin(rad) * current_len
                )
                
                pygame.draw.line(screen, (80, 150, 80), self.pos - pygame.math.Vector2(cam_x, cam_y), end_pos - pygame.math.Vector2(cam_x, cam_y), 8)
