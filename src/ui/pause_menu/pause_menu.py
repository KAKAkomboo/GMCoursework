import pygame
from src.core.settings import screen_width, screen_height

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False

        try:
            self.font_cat = pygame.font.SysFont("timesnewroman", 24)
            self.font_item = pygame.font.SysFont("timesnewroman", 28)
        except:
            self.font_cat = pygame.font.SysFont(None, 24)
            self.font_item = pygame.font.SysFont(None, 28)

        self.categories = [
            ("Inventory", "inventory"),
            ("Options", "settings"),
            ("Quit Game", "menu")
        ]
        self.selected_index = 0

        self.top_bar_height = 80
        self.icon_spacing = 150
        
        self.recalculate_layout()

    def recalculate_layout(self):
        current_w, current_h = self.screen.get_size()
        self.start_x = (current_w - (len(self.categories) * self.icon_spacing)) // 2

    def show(self):
        self.visible = True
        self.selected_index = 0
        self.recalculate_layout()

    def hide(self):
        self.visible = False

    def draw(self):
        if not self.visible:
            return
            
        current_w, current_h = self.screen.get_size()

        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        bar_surf = pygame.Surface((current_w, self.top_bar_height), pygame.SRCALPHA)
        bar_surf.fill((20, 20, 20, 230))
        self.screen.blit(bar_surf, (0, 40))

        pygame.draw.line(self.screen, (100, 100, 100), (0, 40), (current_w, 40), 2)
        pygame.draw.line(self.screen, (100, 100, 100), (0, 40 + self.top_bar_height), (current_w, 40 + self.top_bar_height), 2)

        for i, (name, action) in enumerate(self.categories):
            x = self.start_x + i * self.icon_spacing
            y = 40 + (self.top_bar_height // 2)
            
            is_selected = (i == self.selected_index)
            color = (255, 255, 255) if is_selected else (100, 100, 100)
            
            text = self.font_cat.render(name, True, color)
            rect = text.get_rect(center=(x + self.icon_spacing // 2, y))
            
            self.screen.blit(text, rect)

            if is_selected:
                pygame.draw.line(self.screen, (200, 50, 50), (rect.left, rect.bottom + 5), (rect.right, rect.bottom + 5), 2)

        hint_text = self.font_item.render("Press ENTER to Select", True, (200, 200, 200))
        hint_rect = hint_text.get_rect(center=(current_w // 2, current_h - 50))
        self.screen.blit(hint_text, hint_rect)

    def handle_ev(self, events):
        if not self.visible:
            return None
            
        action = None
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.selected_index = (self.selected_index - 1) % len(self.categories)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.selected_index = (self.selected_index + 1) % len(self.categories)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    action = self.categories[self.selected_index][1]
                elif event.key == pygame.K_ESCAPE:
                    pass
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                if 40 <= my <= 40 + self.top_bar_height:
                    for i in range(len(self.categories)):
                        x = self.start_x + i * self.icon_spacing
                        rect = pygame.Rect(x, 40, self.icon_spacing, self.top_bar_height)
                        if rect.collidepoint(mx, my):
                            self.selected_index = i
                            action = self.categories[i][1]
                            break

        return action
