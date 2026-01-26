import pygame
from src.core.settings import WHITE

class InventoryPanel:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.font_title = pygame.font.SysFont("arial", 32)
        self.font = pygame.font.SysFont("arial", 24)

        self.cell_w, self.cell_h = 80, 80
        self.cols, self.rows = 6, 3

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def draw(self):
        if not self.visible: return
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("Inventory", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 120)))

        start_x = self.screen.get_width() // 2 - (self.cols * self.cell_w + (self.cols - 1) * 10) // 2
        start_y = 200

        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(
                    start_x + c * (self.cell_w + 10),
                    start_y + r * (self.cell_h + 10),
                    self.cell_w,
                    self.cell_h
                )
                pygame.draw.rect(self.screen, (200, 200, 200), rect, 2)

        hint = self.font.render("Press ESC to go back", True, (220, 220, 220))
        self.screen.blit(hint, hint.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() - 80)))

    def handle_ev(self, events):
        if not self.visible: return None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
        return None
