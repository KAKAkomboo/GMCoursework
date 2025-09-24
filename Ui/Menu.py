# GAME MENU

import pygame
from Settings import *
from Buttons import *

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