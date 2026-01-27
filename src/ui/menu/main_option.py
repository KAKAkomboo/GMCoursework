import pygame
from src.core.settings import screen_width, screen_height

class MainOption:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        

        try:
            self.font_title = pygame.font.SysFont("timesnewroman", 48, bold=True)
            self.font_item = pygame.font.SysFont("timesnewroman", 32)
        except:
            self.font_title = pygame.font.SysFont(None, 50)
            self.font_item = pygame.font.SysFont(None, 32)


        self.items = [
            "Game Options", 
            "Brightness", 
            "Key Settings", 
            "Network Settings", 
            "PC Settings",
            "Back"
        ]
        self.selected_index = 0
        self.item_rects = []
        
        self.recalculate_layout()

    def recalculate_layout(self):
        current_screen_width, current_screen_height = self.screen.get_size()
        self.panel_w = 600
        self.panel_h = 500
        self.panel_x = (current_screen_width - self.panel_w) // 2
        self.panel_y = (current_screen_height - self.panel_h) // 2

        self.item_rects = []
        start_y = self.panel_y + 100
        spacing = 60
        for i, item in enumerate(self.items):
            text = self.font_item.render(item, True, (255, 255, 255))
            rect = text.get_rect(center=(current_screen_width // 2, start_y + i * spacing))
            self.item_rects.append(rect)

    def show(self):
        self.visible = True
        self.selected_index = 0
        self.recalculate_layout()

    def hide(self):
        self.visible = False

    def draw(self):
        if not self.visible: return

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        panel.fill((20, 20, 20, 230))
        self.screen.blit(panel, (self.panel_x, self.panel_y))

        pygame.draw.rect(self.screen, (100, 100, 100), (self.panel_x, self.panel_y, self.panel_w, self.panel_h), 2)
        pygame.draw.rect(self.screen, (50, 50, 50), (self.panel_x + 4, self.panel_y + 4, self.panel_w - 8, self.panel_h - 8), 1)

        title = self.font_title.render("System", True, (200, 200, 200))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, self.panel_y + 50))
        shadow = self.font_title.render("System", True, (0, 0, 0))
        self.screen.blit(shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for i, item in enumerate(self.items):
            rect = self.item_rects[i]
            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_index)
            
            color = (150, 150, 150)
            if is_selected or is_hovered:
                color = (255, 255, 255)
                # Indicator
                pygame.draw.circle(self.screen, (200, 50, 50), (rect.left - 20, rect.centery), 4)
            
            text = self.font_item.render(item, True, color)
            self.screen.blit(text, rect)

    def handle_ev(self, events):
        if not self.visible: return None
        
        action = None
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.item_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_index = i
                        if self.items[i] == "Back": return "back"
                        # For other items, we can return their name as action or handle logic
                        return self.items[i].lower().replace(" ", "_")

            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self.item_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_index = i

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                elif event.key == pygame.K_RETURN:
                    if self.items[self.selected_index] == "Back": return "back"
                    return self.items[self.selected_index].lower().replace(" ", "_")
                elif event.key == pygame.K_ESCAPE:
                    return "back"

        return None
