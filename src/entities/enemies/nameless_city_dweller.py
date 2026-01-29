import pygame
import math
import random
from .base_enemy import BaseEnemy

class NamelessCityDweller(BaseEnemy):
    def __init__(self, game, pos):
        super().__init__(game, pos, (40, 60), 120, 0.04)
        self.image.fill((100, 100, 80))
        
        self.magic_cooldown = 5000
        self.last_magic = 0
        self.aoe_projectiles = pygame.sprite.Group()

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        now = pygame.time.get_ticks()

        if self.state in ["STAGGER", "CASTING"]:
            return

        if player_dist < 8 and now - self.last_magic > self.magic_cooldown:
            self.start_casting()
        else:
            self.chase_player(dt)

    def start_casting(self):
        self.state = "CASTING"
        self.state_timer = 2000
        self.last_magic = pygame.time.get_ticks()

    def update(self, dt):
        super().update(dt)
        if self.state == "CASTING" and self.state_timer <= 0:
            self.cast_aoe()
            self.state = "IDLE"
            
        self.aoe_projectiles.update()

    def cast_aoe(self):
        for i in range(12):
            angle = i * 30
            # projectile = AbyssMagic(self.pos.x, self.pos.y, angle)
            # self.aoe_projectiles.add(projectile)
        
        if self.game.game_instance:
            self.game.game_instance.trigger_screen_shake(100, 2)

    def take_damage(self, amount):
        if random.random() > 0.7:
            super().take_damage(amount)
        else:
            self.health -= amount
            if self.health <= 0:
                self.die()

    def draw(self, screen, cam_x, cam_y):
        super().draw(screen, cam_x, cam_y)
        self.aoe_projectiles.draw(screen)
