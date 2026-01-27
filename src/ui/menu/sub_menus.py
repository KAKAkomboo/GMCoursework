import pygame
from src.core.settings import screen_width, screen_height

class BaseSubMenu:
    def __init__(self, screen, title):
        self.screen = screen
        self.title_str = title
        try:
            self.font_title = pygame.font.SysFont("timesnewroman", 40, bold=True)
            self.font_item = pygame.font.SysFont("timesnewroman", 28)
        except:
            self.font_title = pygame.font.SysFont(None, 40)
            self.font_item = pygame.font.SysFont(None, 28)
            
        self.recalculate_layout()

    def recalculate_layout(self):
        current_w, current_h = self.screen.get_size()
        self.panel_w = 500
        self.panel_h = 400
        self.panel_x = (current_w - self.panel_w) // 2
        self.panel_y = (current_h - self.panel_h) // 2

    def draw_background(self):

        self.recalculate_layout()
        
        current_w, current_h = self.screen.get_size()

        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        panel.fill((20, 20, 20, 240))
        self.screen.blit(panel, (self.panel_x, self.panel_y))

        pygame.draw.rect(self.screen, (100, 100, 100), (self.panel_x, self.panel_y, self.panel_w, self.panel_h), 2)

        title = self.font_title.render(self.title_str, True, (200, 200, 200))
        title_rect = title.get_rect(center=(current_w // 2, self.panel_y + 40))
        self.screen.blit(title, title_rect)

        hint = self.font_item.render("Press ESC to Back", True, (100, 100, 100))
        hint_rect = hint.get_rect(center=(current_w // 2, self.panel_y + self.panel_h - 30))
        self.screen.blit(hint, hint_rect)

class BrightnessMenu(BaseSubMenu):
    def __init__(self, screen):
        super().__init__(screen, "Brightness")
        self.brightness = 1.0 # 1.0 = Normal, 0.0 = Dark
        self.slider_rect = pygame.Rect(0, 0, 400, 6) # Placeholder, updated in draw
        self.dragging = False

    def draw(self):
        self.draw_background()

        self.slider_rect = pygame.Rect(self.panel_x + 50, self.panel_y + 180, 400, 6)

        pygame.draw.rect(self.screen, (50, 50, 50), self.slider_rect)

        fill_w = int(self.brightness * self.slider_rect.w)
        fill_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y, fill_w, self.slider_rect.h)
        pygame.draw.rect(self.screen, (200, 200, 200), fill_rect)

        knob_x = self.slider_rect.x + fill_w
        pygame.draw.circle(self.screen, (255, 255, 255), (knob_x, self.slider_rect.centery), 10)

        val_text = self.font_item.render(f"{int(self.brightness * 100)}%", True, (255, 255, 255))
        self.screen.blit(val_text, (self.slider_rect.centerx - val_text.get_width()//2, self.slider_rect.y - 40))

    def handle_ev(self, event):
        self.slider_rect = pygame.Rect(self.panel_x + 50, self.panel_y + 180, 400, 6)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            hitbox = self.slider_rect.inflate(20, 20)
            if hitbox.collidepoint(event.pos):
                self.dragging = True
                self.update_val(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_val(event.pos[0])
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.brightness = max(0.0, self.brightness - 0.05)
            elif event.key == pygame.K_RIGHT:
                self.brightness = min(1.0, self.brightness + 0.05)
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def update_val(self, mouse_x):
        rel = (mouse_x - self.slider_rect.x) / self.slider_rect.w
        self.brightness = max(0.0, min(1.0, rel))

class KeySettingsMenu(BaseSubMenu):
    def __init__(self, screen):
        super().__init__(screen, "Controls")
        self.keys = [
            ("Move", "WASD / Arrows"),
            ("Attack", "Left Click"),
            ("Interact", "E"),
            ("Lock On", "TAB"),
            ("Sprint", "L-Shift"),
            ("Heal", "Q (Not impl.)")
        ]

    def draw(self):
        self.draw_background()
        start_y = self.panel_y + 100
        for i, (action, key) in enumerate(self.keys):
            y = start_y + i * 35
            
            act_surf = self.font_item.render(action, True, (180, 180, 180))
            key_surf = self.font_item.render(key, True, (255, 255, 255))
            
            self.screen.blit(act_surf, (self.panel_x + 50, y))
            self.screen.blit(key_surf, (self.panel_x + 300, y))

    def handle_ev(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None

class GameOptionsMenu(BaseSubMenu):
    def __init__(self, screen):
        super().__init__(screen, "Game Options")
        self.options = ["Difficulty: Normal", "Show HUD: On", "Blood: On"]

    def draw(self):
        self.draw_background()
        start_y = self.panel_y + 120
        current_w = self.screen.get_width()
        for i, opt in enumerate(self.options):
            text = self.font_item.render(opt, True, (200, 200, 200))
            rect = text.get_rect(center=(current_w // 2, start_y + i * 50))
            self.screen.blit(text, rect)

    def handle_ev(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None

class PlaceholderMenu(BaseSubMenu):
    def __init__(self, screen, title, msg="Feature not available yet."):
        super().__init__(screen, title)
        self.msg = msg

    def draw(self):
        self.draw_background()
        current_w, current_h = self.screen.get_size()
        text = self.font_item.render(self.msg, True, (150, 150, 150))
        rect = text.get_rect(center=(current_w // 2, current_h // 2))
        self.screen.blit(text, rect)

    def handle_ev(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None
