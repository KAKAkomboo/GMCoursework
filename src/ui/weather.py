import pygame
import random
from src.core.settings import screen_width, screen_height

class RainDrop:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()
        self.y = random.randint(0, h) # Start randomly on screen

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
