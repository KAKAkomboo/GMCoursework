import pygame
from Ui.Buttons import Button
from Settings import screen_width, screen_height, Primary_font, White_color

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 40)

        self.options = ["Settings", "Tasks", "Inventory", "Exit to Main Menu"]
        self.buttons = []

        button_width = 300
        button_height = 60
        spacing = 15
        total_height = len(self.options) * (button_height + spacing)
        start_y = (screen_height - total_height) // 2
        start_x = (screen_width - button_width) // 2

        for i, option in enumerate(self.options):
            y = start_y + i * (button_height + spacing)
            btn = Button(start_x, y, button_width, button_height, option)
            self.buttons.append(btn)

        self.title = Primary_font.render("Paused", True, White_color)
        self.title_rect = self.title.get_rect(center=(screen_width // 2, 100))

    def draw(self):
        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        self.screen.blit(self.title, self.title_rect)

        for btn in self.buttons:
            btn.draw(self.screen)

    def handle_ev(self, events):
        for event in events:
            for i, btn in enumerate(self.buttons):
                if btn.handle_ev(event):
                    if i == 0:
                        return "settings"
                    elif i == 1:
                        return "tasks"
                    elif i == 2:
                        return "inventory"
                    elif i == 3:
                        return "menu"
        return None
