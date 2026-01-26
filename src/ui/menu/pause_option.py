import pygame
from src.ui.elements.button import Button
from src.core.settings import screen_width, WHITE, PURPLE

class PauseOption:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.font_title = pygame.font.SysFont("arial", 32)
        self.font = pygame.font.SysFont("arial", 24)

        self.music_volume = 0.5
        self.slider_rect = pygame.Rect(screen_width // 2 - 200, 200, 400, 8)
        self.knob_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y - 6, 16, 20)
        self.dragging = False

        self.btn_full = Button(screen_width // 2 - 120, 260, 240, 50, "Toggle Fullscreen")
        self.btn_back = Button(screen_width // 2 - 80, 330, 160, 50, "Back")

        self.title = self.font_title.render("Pause Settings", True, WHITE)

    def show(self): self.visible = True
    def hide(self): self.visible = False

    def draw(self):
        if not self.visible: return
        panel = pygame.Surface((600, 300), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 180))
        px = (screen_width - 600) // 2
        self.screen.blit(panel, (px, 140))

        tx = (screen_width - self.title.get_width()) // 2
        self.screen.blit(self.title, (tx, 160))

        label = self.font.render("Music Volume", True, WHITE)
        lx = (screen_width - label.get_width()) // 2
        self.screen.blit(label, (lx, 190))

        pygame.draw.rect(self.screen, WHITE, self.slider_rect)
        knob_x = self.slider_rect.x + int(self.music_volume * self.slider_rect.w) - self.knob_rect.w // 2
        self.knob_rect.x = max(self.slider_rect.x, min(knob_x, self.slider_rect.right - self.knob_rect.w))
        pygame.draw.rect(self.screen, PURPLE, self.knob_rect, border_radius=4)

        self.btn_full.draw(self.screen)
        self.btn_back.draw(self.screen)

    def handle_ev(self, events):
        if not self.visible: return None
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.knob_rect.collidepoint(event.pos) or self.slider_rect.collidepoint(event.pos):
                    self.dragging = True
                    rel = (event.pos[0] - self.slider_rect.x) / float(self.slider_rect.w)
                    self.music_volume = max(0.0, min(1.0, rel))
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                rel = (event.pos[0] - self.slider_rect.x) / float(self.slider_rect.w)
                self.music_volume = max(0.0, min(1.0, rel))

            if self.btn_full.handle_ev(event):
                return "toggle_fullscreen"
            if self.btn_back.handle_ev(event):
                return "back"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
        return None
