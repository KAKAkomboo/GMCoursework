import pygame
from src.core.settings import screen_width, screen_height, Black_color
from src.ui.elements.button import Button

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Start", "Options", "Quit"]
        self.selected = 0

        bw, bh = 240, 40
        spacing = 20
        total_h = len(self.options) * bh + (len(self.options) - 1) * spacing
        start_y = int(screen_height * 0.8) - total_h // 2
        start_x = (screen_width - bw) // 2

        try:
            img = pygame.image.load("assets/images/Background_Images/bggame.png").convert_alpha()
            self.bg_image = pygame.transform.scale(img, (screen_width, screen_height))
        except Exception as e:
            print("Background load failed:", e)
            self.bg_image = None

        self.buttons = []
        for i, option in enumerate(self.options):
            y = start_y + i * (bh + spacing)
            self.buttons.append(Button(start_x, y, bw, bh, option))

    def draw(self):
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill(Black_color)

        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            button.hover = button.rect.collidepoint(mouse_pos)
            button.focused = (i == self.selected)
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
