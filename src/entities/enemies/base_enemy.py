import pygame
import math
import random

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, game, pos, size, health, speed):
        super().__init__()
        self.game = game
        self.pos = pygame.math.Vector2(pos)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)
        
        self.max_health = health
        self.health = health
        self.speed = speed
        self.alive = True

        self.state = "IDLE"
        self.state_timer = 0

        self.rally_timer = 0
        self.rally_duration = 2000
        
        self.step_dodge_cooldown = 3000
        self.last_dodge = 0
        
        self.vision_range = 15
        self.attack_range = 1.5
        
        self.invincible = False
        self.invincible_timer = 0

    def update(self, dt):
        if not self.alive: return

        self.update_timers(dt)
        self.run_ai(dt)
        
        self.rect.center = self.pos

    def run_ai(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        player_dist = self.pos.distance_to(player_pos)
        
        if self.state in ["STAGGER", "DODGE", "ATTACK"]:
            return

        if player_dist < self.attack_range:
            self.state = "ATTACK"
            self.start_attack()
        elif player_dist < self.vision_range:
            self.state = "CHASE"
            self.chase_player(dt)
        else:
            self.state = "IDLE"

    def chase_player(self, dt):
        player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
        direction = (player_pos - self.pos).normalize()
        self.pos += direction * self.speed * (dt / 16.0)

    def start_attack(self):
        pass

    def take_damage(self, amount):
        if self.invincible: return
        
        self.health -= amount
        self.rally_timer = self.rally_duration
        
        if self.health <= 0:
            self.die()
        else:
            self.trigger_stagger(200)

    def trigger_stagger(self, duration):
        self.state = "STAGGER"
        self.state_timer = duration
        self.invincible = True
        self.invincible_timer = duration

    def update_timers(self, dt):
        if self.rally_timer > 0:
            self.rally_timer -= dt
        if self.state_timer > 0:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "IDLE"
        if self.invincible_timer > 0:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False

    def die(self):
        self.alive = False
        self.kill()
        self.game.player.add_currency(50)

    def step_dodge(self):
        now = pygame.time.get_ticks()
        if now - self.last_dodge > self.step_dodge_cooldown:
            self.last_dodge = now
            self.state = "DODGE"
            self.state_timer = 300
            player_pos = pygame.math.Vector2(self.game.player.x, self.game.player.y)
            direction = (player_pos - self.pos).normalize()
            self.dodge_dir = direction.rotate(random.choice([-90, 90]))

    def draw(self, screen, cam_x, cam_y):
        if self.alive:
            screen.blit(self.image, self.rect.move(-cam_x, -cam_y))
