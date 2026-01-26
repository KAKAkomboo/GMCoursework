import pygame
from src.core.settings import WHITE

class TasksPanel:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.font_title = pygame.font.SysFont("arial", 32)
        self.font = pygame.font.SysFont("arial", 24)

        self.stub_lines = [
            "- Reach the first bonfire",
            "- Defeat the Hollow Knight",
            "- Collect 5 soul fragments",
        ]

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def draw(self):
        if not self.visible: return
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("Tasks", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, 120)))

        y = 200
        for line in self.stub_lines:
            txt = self.font.render(line, True, (230, 230, 230))
            self.screen.blit(txt, (self.screen.get_width() // 2 - 220, y))
            y += 30

    def handle_ev(self, events):
        if not self.visible: return None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
        return None
