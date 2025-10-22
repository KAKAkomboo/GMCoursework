from Ui.Buttons import *
from Ui.Slider import Slider
import pygame
from Settings import *


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Start", "Options", "Quit"]
        self.selected = 0
        self.font = pygame.font.SysFont("arial", 40)

        self.button_width = 200
        self.button_height = 60
        self.button_spacing = 10
        self.start_y = (screen_height - (len(self.options) * self.button_height) + (
                len(self.options) - 1) * self.button_spacing) // 2
        self.start_x = (screen_width - self.button_width) // 2

        self.buttons = []
        for i, option in enumerate(self.options):
            y = self.start_y + i * (self.button_height + self.button_spacing)
            button = Button(self.start_x, y, self.button_width, self.button_height, option)
            self.buttons.append(button)

        self.title = Primary_font.render("Bebebbe", True, White_color)
        self.title_rect = self.title.get_rect(center=(screen_width // 2, 100))

        pygame.mixer.init()
        pygame.mixer.music.load('assets/sounds/sound_01.mp3')
        pygame.mixer.music.play(-1)

    def draw(self):
        self.screen.fill(Black_color)
        self.screen.blit(self.title, self.title_rect)

        mouse_pos = pygame.mouse.get_pos()

        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                button.hovered = True
                self.selected = i
            else:
                button.hovered = (i == self.selected)

            button.draw(self.screen)

    def handle_ev(self, events):
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
                    if action in ["start", "quit"]:
                        pygame.mixer.music.stop()
                    return action
                elif event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return "quit"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.buttons:
                    if button.is_clicked(event.pos):
                        idx = self.buttons.index(button)
                        self.selected = idx
                        action = self._get_action(idx)
                        if action in ["start", "quit"]:
                            pygame.mixer.music.stop()
                        return action
        return None

    def _get_action(self, index):
        if index == 0:
            return "start"
        elif index == 1:
            return "options"
        elif index == 2:
            return "quit"
        return None



class OptionsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Sound", "Music", "Back"]
        self.selected = 0
        self.font = pygame.font.SysFont("arial", 40)

        self.music_volume = 1.0

        slider_width = 300
        slider_height = 10
        slider_x = (screen_width - slider_width) // 2
        self.music_slider = Slider(slider_x, 300, slider_width, slider_height, self.music_volume)

        self.fullscreen_button = Button(screen_width // 2 - 150, 370, 300, 60, "Toggle Fullscreen")

        self.back_button = Button(screen_width // 2 - 100, 450, 200, 60, "Back")

        self.title = Primary_font.render("Settings", True, White_color)
        self.title_rect = self.title.get_rect(center=(screen_width // 2, 100))

    def draw(self):
        self.screen.fill(Black_color)
        self.screen.blit(self.title, self.title_rect)

        music_text = self.font.render("Music Volume", True, White_color)
        self.screen.blit(music_text, (self.music_slider.rect.x, self.music_slider.rect.y - 40))

        self.music_slider.draw(self.screen)

        self.fullscreen_button.draw(self.screen)

        self.back_button.draw(self.screen)



    def handle_ev(self, events):
        for event in events:
            self.music_slider.handle_event(event)
            if self.back_button.handle_ev(event):
                return "back"
            if self.fullscreen_button.handle_ev(event):
                return "toggle_fullscreen"
        pygame.mixer.music.set_volume(self.music_slider.value)

        return None

    def _get_action(self, index):
        if index == 0:
            return "back"
        return None