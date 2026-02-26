import pygame
import random
from src.core.settings import screen_width, screen_height

class RainDrop:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()
        self.y = random.randint(0, h)

    def reset(self):
        self.x = random.randint(0, self.w)
        self.y = random.randint(-50, -10)
        self.speed = random.randint(10, 20)
        self.length = random.randint(10, 20)
        self.thickness = random.randint(1, 2)
        self.wind = 2

    def update(self):
        self.y += self.speed
        self.x += self.wind
        if self.y > self.h:
            self.reset()

    def draw(self, screen):
        pygame.draw.line(screen, (150, 150, 180, 100), (self.x, self.y), (self.x + self.wind, self.y + self.length), self.thickness)

class Rain:
    def __init__(self, screen, intensity=100):
        self.screen = screen
        self.drops = [RainDrop(screen.get_width(), screen.get_height()) for _ in range(intensity)]

    def update(self):
        for drop in self.drops:
            drop.update()

    def draw(self):
        for drop in self.drops:
            drop.draw(self.screen)

    def recalculate_layout(self):
        w, h = self.screen.get_size()
        for drop in self.drops:
            drop.w = w
            drop.h = h

class FogParticle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)

    def reset(self):
        self.x = -100
        self.y = random.randint(0, self.h)
        self.speed = random.uniform(0.2, 0.8)
        self.size = random.randint(100, 300)
        self.alpha = random.randint(20, 60)

    def update(self):
        self.x += self.speed
        if self.x > self.w + 100:
            self.reset()
            self.x = -100 # Reset to left side

    def draw(self, screen):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 200, 220, self.alpha), (self.size//2, self.size//2), self.size//2)
        screen.blit(s, (int(self.x), int(self.y)))

class Fog:
    def __init__(self, screen, density=20):
        self.screen = screen
        self.particles = [FogParticle(screen.get_width(), screen.get_height()) for _ in range(density)]

    def update(self):
        for p in self.particles:
            p.update()

    def draw(self):
        for p in self.particles:
            p.draw(self.screen)

    def recalculate_layout(self):
        w, h = self.screen.get_size()
        for p in self.particles:
            p.w = w
            p.h = h
