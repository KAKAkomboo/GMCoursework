# Ui/Menu.py
import pygame
from Ui.Buttons import Button
from Ui.Slider import Slider
from Settings import screen_width, screen_height, Primary_font, White_color, Black_color

# Initialize mixer once at module import
pygame.mixer.init()
try:
    pygame.mixer.music.load('assets/sounds/sound_01.mp3')
except Exception:
    # If the file is missing or fails to load, ignore and continue
    pass


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Start", "Options", "Quit"]
        self.selected = 0
        self.font = pygame.font.SysFont("arial", 40)

        self.button_width = 200
        self.button_height = 60
        self.button_spacing = 10
        total_h = len(self.options) * self.button_height + (len(self.options) - 1) * self.button_spacing
        self.start_y = (screen_height - total_h) // 2
        self.start_x = (screen_width - self.button_width) // 2

        self.buttons = []
        for i, option in enumerate(self.options):
            y = self.start_y + i * (self.button_height + self.button_spacing)
            button = Button(self.start_x, y, self.button_width, self.button_height, option)
            self.buttons.append(button)

        # Title uses Primary_font from Settings
        self.title = Primary_font.render("Bebebbe", True, White_color)
        self.title_rect = self.title.get_rect(center=(screen_width // 2, 100))

        # Start music if loaded
        try:
            pygame.mixer.music.play(-1)
        except Exception:
            pass

    def draw(self):
        self.screen.fill(Black_color)
        self.screen.blit(self.title, self.title_rect)

        mouse_pos = pygame.mouse.get_pos()

        for i, button in enumerate(self.buttons):
            hovered = button.rect.collidepoint(mouse_pos)
            # keyboard selection overrides hover highlight
            if hovered:
                button.hovered = True
                self.selected = i
            else:
                button.hovered = (i == self.selected)
            button.draw(self.screen)

    def handle_ev(self, events):
        """
        Process events and return one of: "start", "options", "quit", or None.
        Stops music on start/quit.
        """
        action = None
        for event in events:
            # Let buttons process the event (mouse hover/click)
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

            if action:
                # stop music only for start or quit
                if action in ("start", "quit"):
                    try:
                        pygame.mixer.music.stop()
                    except Exception:
                        pass
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
        self.font = pygame.font.SysFont("arial", 40)

        # Music slider
        self.music_volume = 1.0
        slider_width = 300
        slider_height = 10
        slider_x = (screen_width - slider_width) // 2
        self.music_slider = Slider(slider_x, 300, slider_width, slider_height, self.music_volume)

        # Fullscreen toggle and back button
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
        """
        Returns "back", "toggle_fullscreen", or None.
        Updates pygame.mixer.music volume from the slider.
        """
        for event in events:
            self.music_slider.handle_event(event)
            if self.back_button.handle_ev(event):
                return "back"
            if self.fullscreen_button.handle_ev(event):
                return "toggle_fullscreen"

        # Apply slider value to music volume
        try:
            pygame.mixer.music.set_volume(self.music_slider.value)
        except Exception:
            pass

        return None
