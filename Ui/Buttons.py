import pygame
from Settings import *


class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = White_color
        self.hover_color = Primary_color
        self.text_color = Black_color
        self.border_color = Black_color
        self.font = Primary_font
        self.hovered = False
        self.border_radius = 15

    def draw(self, screen):
        fill_color = self.hover_color if self.hovered else self.color

        pygame.draw.rect(screen, fill_color, self.rect, border_radius=self.border_radius)

        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=self.border_radius)

        text_surface = self.font.render(self.text, True, self.text_color)
        shadow_color = (50, 50, 50)
        shadow_surface = self.font.render(self.text, True, shadow_color)

        text_rect = text_surface.get_rect(center=self.rect.center)
        shadow_rect = shadow_surface.get_rect(
            center=(text_rect.centerx + 2, text_rect.centery + 2))

        screen.blit(shadow_surface, shadow_rect)

        screen.blit(text_surface, text_rect)

    def handle_ev(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and event.button == 1:
                return True
        return False

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

