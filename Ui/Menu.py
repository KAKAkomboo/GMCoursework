# GAME MENU

import pygame
from Settings import *
from Ui.Buttons import *

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Start", "Options", "Quit"]
        self.selected = 0
        self.font = pygame.font.SysFont("arial", 40)

        self.button_width = 200
        self.button_height = 60
        self.button_s = 10
        self.start_y = (screen_height - (len(self.options) * self.button_height) + (len(self.options) - 1) * self.button_s) // 2
        self.start_x = (screen_width - self.button_width) // 2

        self.buttons = []
        for i, option in enumerate(self.options):
            y = self.start_y + i * (self.button_height + self.button_s)
            button = Button(self.start_x, y, self.button_width, self.button_height, option)
            self.buttons.append(button)

        self.title = Primary_font.render("Bebebbe", True, White_color)
        self.title_rect = self.title.get_rect(center=(screen_width//2, 100))

    def draw(self):
        self.screen.fill(Black_color)

        self.screen.blit(self.title, self.title_rect)

        for i, button in enumerate(self.buttons):
            if i == self.selected:
                button.color = Secondary_color
                button.hover_color = Primary_color
                button.hovered = True
            else:
                button.color = Primary_color
                button.hover_color = Secondary_color
                button.hovered = False
                button.draw(self.screen)

    def handle_ev(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self._get_action(self)
                elif event.key == pygame.K_ESCAPE:
                    return "quit"

            for button in self.buttons:
                if button.handle_ev(event):
                    idx = self.buttons.index(button)
                    self.selected = idx
                    return self._get_action(idx)

        return None

    def _get_action(self, index):
        if index == 0:
            return "start"
        elif index == 1:
            return "options"
        elif index == 2:
            return "quit"
        return None