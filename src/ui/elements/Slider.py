import pygame

class Slider:
    def __init__(self, x, y, width, height, value=1.0, color=(200, 200, 200), handle_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.handle_color = handle_color
        self.handle_rect = pygame.Rect(x + value * (width - 10), y - 5, 10, height + 10)
        self.value = value
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, self.handle_color, self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.handle_rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.handle_rect.x = max(self.rect.x, min(event.pos[0] - 5, self.rect.right - 10))
            self.value = (self.handle_rect.x - self.rect.x) / (self.rect.width - 10)
