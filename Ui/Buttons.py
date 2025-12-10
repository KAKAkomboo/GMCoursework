import pygame

class Button:
    def __init__(self, x, y, width, height, text, font_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.hover = False
        self.focused = False

        if font_path:
            self.font = pygame.font.Font(font_path, 24)
        else:
            self.font = pygame.font.SysFont("timesnewroman", 24, bold=True)

        self.text_color = (255, 255, 255)
        self.hover_text_color = (255, 200, 50)

        self.gradient = pygame.Surface((width, height))
        for y_pos in range(height):
            r = int(40 + (y_pos / height) * 40)
            g = int(30 + (y_pos / height) * 30)
            b = int(20 + (y_pos / height) * 20)
            pygame.draw.line(self.gradient, (r, g, b), (0, y_pos), (width, y_pos))
        self.gradient.set_alpha(180)

    def draw(self, surface):
        if self.hover:
            surface.blit(self.gradient, self.rect.topleft)

        color = self.hover_text_color if self.hover else self.text_color
        text_surf = self.font.render(self.text, True, color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

        if self.focused and not self.hover:
            pygame.draw.rect(surface, (200, 170, 90), self.rect, 1)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def handle_ev(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
