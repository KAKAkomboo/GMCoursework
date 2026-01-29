import pygame

class Cutscene:
    def __init__(self, screen, lines, font_size=32, color=(200, 200, 200), speed=1.5):
        self.screen = screen
        self.lines = lines
        self.font = pygame.font.SysFont("timesnewroman", font_size)
        self.color = color
        self.speed = speed 

        self.line_index = 0
        self.char_index = 0.0
        self.is_active = True
        self.is_line_complete = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if not self.is_line_complete:
                    self.char_index = len(self.lines[self.line_index])
                else:
                    self.next_line()

    def next_line(self):
        if self.line_index < len(self.lines) - 1:
            self.line_index += 1
            self.char_index = 0.0
            self.is_line_complete = False
        else:
            self.is_active = False

    def update(self, dt):
        if not self.is_active:
            return False

        if self.char_index < len(self.lines[self.line_index]):
            self.char_index += self.speed * (dt / 16.0)
        else:
            self.is_line_complete = True
        
        return True

    def draw(self):
        if not self.is_active:
            return

        self.screen.fill((0, 0, 0))
        
        current_line_text = self.lines[self.line_index]
        visible_text = current_line_text[:int(self.char_index)]

        self.draw_text_wrapped(visible_text)

        if self.is_line_complete:
            icon_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.polygon(icon_surf, (200, 200, 200), [(0, 0), (10, 5), (0, 10)])
            self.screen.blit(icon_surf, (self.screen.get_width() - 40, self.screen.get_height() - 40))

    def draw_text_wrapped(self, text):
        words = text.split(' ')
        lines = []
        current_line = []
        max_width = self.screen.get_width() * 0.8
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = self.font.size(test_line)
            if w < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))

        total_height = len(lines) * self.font.get_height()
        start_y = (self.screen.get_height() - total_height) // 2
        
        for i, line in enumerate(lines):
            surf = self.font.render(line, True, self.color)
            rect = surf.get_rect(center=(self.screen.get_width() // 2, start_y + i * self.font.get_height()))
            self.screen.blit(surf, rect)
