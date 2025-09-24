import pygame
from Settings import *

class Button:
    def __init__(self, x, y, width, height, text):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = White_color
        self.hover_color = Primary_color
        self.text_color = Black_color
        self.font = Primary_font
        self.hovered = False

    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color