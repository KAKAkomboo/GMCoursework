import pygame
from Ui.Buttons import Button
from Settings import screen_width, screen_height, Primary_font, White_color, Black_color

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Start", "Options", "Quit"]
        self.selected = 0
        self.font = pygame.font.SysFont("arial", 40)

        self.buttons = []
        bw, bh, spacing = 200, 60, 10
        total_h = len(self.options) * bh + (len(self.options) - 1) * spacing
        start_y = (screen_height - total_h) // 2
        start_x = (screen_width - bw) // 2

        for i, option in enumerate(self.options):
            y = start_y + i * (bh + spacing)
            self.buttons.append(Button(start_x, y, bw, bh, option))

        self.title = Primary_font.render("Game Title", True, White_color)
        self.title_rect = self.title.get_rect(center=(screen_width // 2, 100))

    def draw(self):
        self.screen.fill(Black_color)
        self.screen.blit(self.title, self.title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            button.hover = button.rect.collidepoint(mouse_pos) or (i == self.selected)
            button.draw(self.screen)

    def handle_ev(self, events):
        action = None
        for event in events:
            for button in self.buttons:
                button.handle_ev(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    action = self._get_action(self.selected)
                elif event.key == pygame.K_ESCAPE:
                    action = "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, button in enumerate(self.buttons):
                    if button.is_clicked(event.pos):
                        self.selected = i
                        action = self._get_action(i)
                        break

        return action

    def _get_action(self, index):
        return ["start", "options", "quit"][index]
