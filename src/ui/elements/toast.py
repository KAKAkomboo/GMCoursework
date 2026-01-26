import pygame
import time

class Toast:
    def __init__(self):
        self.message = ""
        self.until = 0

    def show(self, message, duration_ms):
        self.message = message
        self.until = int(time.time() * 1000) + duration_ms

    def draw(self, screen, font_small):
        now = int(time.time() * 1000)
        if now > self.until or not self.message:
            return
        t = font_small.render(self.message, True, (255, 255, 255))
        pad = 10
        surf = pygame.Surface((t.get_width() + pad * 2, t.get_height() + pad * 2), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 180))
        x = screen.get_width() // 2 - surf.get_width() // 2
        y = 30
        screen.blit(surf, (x, y))
        screen.blit(t, (x + pad, y + pad))
