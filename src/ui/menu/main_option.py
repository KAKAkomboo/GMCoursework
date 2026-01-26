import pygame
from src.ui.elements.button import Button
from src.core.settings import screen_width, WHITE

class MainOption:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.font_title = pygame.font.SysFont("arial", 32)

        self.title = self.font_title.render("System", True, WHITE)
        self.options = [
            Button(screen_width // 2 - 120, 180, 240, 50, "Options"),
            Button(screen_width // 2 - 120, 240, 240, 50, "Brightness"),
            Button(screen_width // 2 - 120, 300, 240, 50, "Key Settings"),
            Button(screen_width // 2 - 120, 360, 240, 50, "Network Settings"),
            Button(screen_width // 2 - 120, 420, 240, 50, "PC Settings"),
        ]
        self.btn_back = Button(screen_width // 2 - 80, 490, 160, 50, "Back")

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def draw(self):
        if not self.visible: return
        panel = pygame.Surface((600, 420), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        px = (screen_width - 600) // 2
        self.screen.blit(panel, (px, 140))

        tx = (screen_width - self.title.get_width()) // 2
        self.screen.blit(self.title, (tx, 150))

        for btn in self.options:
            btn.draw(self.screen)
        self.btn_back.draw(self.screen)

    def handle_ev(self, events):
        if not self.visible: return None
        for event in events:
            for btn in self.options:
                if btn.handle_ev(event):
                    return btn.text.lower().replace(" ", "_")
            if self.btn_back.handle_ev(event):
                return "back"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
        return None
