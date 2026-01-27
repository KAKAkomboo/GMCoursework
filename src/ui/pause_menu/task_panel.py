import pygame
from src.core.settings import WHITE

class TasksPanel:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        try:
            self.font_title = pygame.font.SysFont("timesnewroman", 32, bold=True)
            self.font = pygame.font.SysFont("timesnewroman", 24)
        except:
            self.font_title = pygame.font.SysFont("arial", 32)
            self.font = pygame.font.SysFont("arial", 24)

        self.stub_lines = [
            "- Reach the first bonfire",
            "- Defeat the Hollow Knight",
            "- Collect 5 soul fragments",
        ]
        self.recalculate_layout()

    def recalculate_layout(self):
        pass

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def draw(self):
        if not self.visible: return
        current_w, current_h = self.screen.get_size()

        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("Tasks", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(current_w // 2, 120)))

        y = 200
        for line in self.stub_lines:
            txt = self.font.render(line, True, (230, 230, 230))
            self.screen.blit(txt, (current_w // 2 - 220, y))
            y += 30

    def handle_ev(self, events):
        if not self.visible: return None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
        return None
