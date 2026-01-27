import pygame
from src.core.settings import screen_width, screen_height

class PauseOption:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False

        try:
            self.font_title = pygame.font.SysFont("timesnewroman", 48, bold=True)
            self.font_item = pygame.font.SysFont("timesnewroman", 32)
            self.font_small = pygame.font.SysFont("timesnewroman", 24)
        except:
            self.font_title = pygame.font.SysFont(None, 50)
            self.font_item = pygame.font.SysFont(None, 32)
            self.font_small = pygame.font.SysFont(None, 24)

        self.music_volume = 0.5

        self.items = ["Toggle Fullscreen", "Back"]
        self.selected_index = 0
        self.item_rects = []
        
        self.recalculate_layout()

    def recalculate_layout(self):
        current_w, current_h = self.screen.get_size()

        self.panel_w = 600
        self.panel_h = 400
        self.panel_x = (current_w - self.panel_w) // 2
        self.panel_y = (current_h - self.panel_h) // 2

        self.slider_w = 300
        self.slider_h = 4
        self.slider_rect = pygame.Rect(self.panel_x + (self.panel_w - self.slider_w) // 2, self.panel_y + 150, self.slider_w, self.slider_h)
        self.knob_radius = 10

        self.item_rects = []
        start_y = self.panel_y + 220
        spacing = 60
        for i, item in enumerate(self.items):
            text = self.font_item.render(item, True, (255, 255, 255))
            rect = text.get_rect(center=(current_w // 2, start_y + i * spacing))
            self.item_rects.append(rect)

    def show(self):
        self.visible = True
        self.selected_index = 0
        self.recalculate_layout()

    def hide(self):
        self.visible = False

    def draw(self):
        if not self.visible: return

        current_w, current_h = self.screen.get_size()
        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Surface((self.panel_w, self.panel_h), pygame.SRCALPHA)
        panel.fill((20, 20, 20, 230))
        self.screen.blit(panel, (self.panel_x, self.panel_y))

        pygame.draw.rect(self.screen, (100, 100, 100), (self.panel_x, self.panel_y, self.panel_w, self.panel_h), 2)
        pygame.draw.rect(self.screen, (50, 50, 50), (self.panel_x + 4, self.panel_y + 4, self.panel_w - 8, self.panel_h - 8), 1)

        title = self.font_title.render("Options", True, (200, 200, 200))
        title_rect = title.get_rect(center=(current_w // 2, self.panel_y + 50))
        shadow = self.font_title.render("Options", True, (0, 0, 0))
        self.screen.blit(shadow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title, title_rect)

        label = self.font_small.render("Music Volume", True, (180, 180, 180))
        label_rect = label.get_rect(center=(current_w // 2, self.slider_rect.y - 30))
        self.screen.blit(label, label_rect)

        pygame.draw.rect(self.screen, (80, 80, 80), self.slider_rect)
        fill_w = int(self.music_volume * self.slider_w)
        fill_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y, fill_w, self.slider_h)
        pygame.draw.rect(self.screen, (200, 200, 200), fill_rect)

        knob_x = self.slider_rect.x + fill_w
        knob_y = self.slider_rect.centery
        pygame.draw.circle(self.screen, (255, 255, 255), (knob_x, knob_y), self.knob_radius)
        pygame.draw.circle(self.screen, (100, 100, 100), (knob_x, knob_y), self.knob_radius, 1)

        mouse_pos = pygame.mouse.get_pos()
        for i, item in enumerate(self.items):
            rect = self.item_rects[i]
            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected_index)
            
            color = (150, 150, 150)
            if is_selected or is_hovered:
                color = (255, 255, 255)
                pygame.draw.circle(self.screen, (200, 50, 50), (rect.left - 20, rect.centery), 4)
            
            text = self.font_item.render(item, True, color)
            self.screen.blit(text, rect)

    def handle_ev(self, events):
        if not self.visible: return None
        
        action = None
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                slider_hitbox = self.slider_rect.inflate(20, 20)
                if slider_hitbox.collidepoint(event.pos):
                    self.dragging = True
                    rel = (event.pos[0] - self.slider_rect.x) / float(self.slider_rect.w)
                    self.music_volume = max(0.0, min(1.0, rel))
                    try:
                        pygame.mixer.music.set_volume(self.music_volume)
                    except: pass

                for i, rect in enumerate(self.item_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_index = i
                        if i == 0: return "toggle_fullscreen"
                        elif i == 1: return "back"

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    rel = (event.pos[0] - self.slider_rect.x) / float(self.slider_rect.w)
                    self.music_volume = max(0.0, min(1.0, rel))
                    try:
                        pygame.mixer.music.set_volume(self.music_volume)
                    except: pass

                for i, rect in enumerate(self.item_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_index = i

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                elif event.key == pygame.K_LEFT:
                    self.music_volume = max(0.0, self.music_volume - 0.1)
                    try: pygame.mixer.music.set_volume(self.music_volume)
                    except: pass
                elif event.key == pygame.K_RIGHT:
                    self.music_volume = min(1.0, self.music_volume + 0.1)
                    try: pygame.mixer.music.set_volume(self.music_volume)
                    except: pass
                elif event.key == pygame.K_RETURN:
                    if self.selected_index == 0: return "toggle_fullscreen"
                    elif self.selected_index == 1: return "back"
                elif event.key == pygame.K_ESCAPE:
                    return "back"

        return None
