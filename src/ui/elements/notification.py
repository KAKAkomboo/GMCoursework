import pygame

class Notification:
    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.text = ""
        self.timer = 0
        self.duration = 4000
        self.width = 400
        self.height = 60
        self.y_pos = -self.height
        self.target_y = 20
        
        try:
            self.font = pygame.font.SysFont("timesnewroman", 22)
        except:
            self.font = pygame.font.SysFont(None, 24)

    def show(self, text):
        self.text = text
        self.active = True
        self.timer = self.duration

    def update(self, dt):
        if not self.active:
            return

        if self.timer > self.duration - 500: # Фаза появи
            self.y_pos = min(self.target_y, self.y_pos + 5)
        elif self.timer < 500: # Фаза зникнення
            self.y_pos = max(-self.height, self.y_pos - 5)
        
        self.timer -= dt
        if self.timer <= 0:
            self.active = False
            self.y_pos = -self.height

    def draw(self):
        if not self.active:
            return
            
        current_w = self.screen.get_width()
        x_pos = (current_w - self.width) // 2

        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        s.fill((20, 20, 25, 200))

        text_surf = self.font.render(self.text, True, (220, 220, 220))
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        s.blit(text_surf, text_rect)

        pygame.draw.rect(s, (150, 120, 50), s.get_rect(), 2)
        
        self.screen.blit(s, (x_pos, self.y_pos))
