import pygame
from Settings import WHITE, GRAY

class Button:
    def __init__(self, x, y, w, h, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = pygame.font.SysFont("arial", 24)
        self.hover = False

    def draw(self, screen):
        color = GRAY if self.hover else (80, 80, 80)
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)

        if self.text:
            label = self.font.render(self.text, True, WHITE)
            lx = self.rect.x + (self.rect.w - label.get_width()) // 2
            ly = self.rect.y + (self.rect.h - label.get_height()) // 2
            screen.blit(label, (lx, ly))

    def handle_ev(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
