# GAME MENU

import pygame
from setting import *

pygame.init()

class Menu:
    def __init__(self, scren):
        self.screen = scren
        self.option = ["Start", "Options", "Quit"]
        self.selected = 0
        self.font = pygame.font.SysFont("arial", 40)