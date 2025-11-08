import pygame
from Settings import tile_size, NPC_SPEED, NPC_DIALOG_DISTANCE, DIALOG_BOX_COLOR, DIALOG_TEXT_COLOR, Primary_font


class NPC:
    def __init__(self, x, y, image_path, dialog_text):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.speed = NPC_SPEED
        self.dialog_text = dialog_text
        self.show_dialog = False

    def update(self, player_x, player_y):
        self.x += self.speed
        if self.x > 100 or self.x < 0:
            self.speed *= -1

        distance = ((self.x - player_x) ** 2 + (self.y - player_y) ** 2) ** 0.5
        if distance < NPC_DIALOG_DISTANCE:
            self.show_dialog = True
        else:
            self.show_dialog = False

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x * tile_size - camera_x, self.y * tile_size - camera_y))
        if self.show_dialog:
            box_rect = pygame.Rect(50, screen.get_height() - 150, screen.get_width() - 100, 100)
            pygame.draw.rect(screen, DIALOG_BOX_COLOR, box_rect)
            text = Primary_font.render(self.dialog_text, True, DIALOG_TEXT_COLOR)
            screen.blit(text, (box_rect.x + 10, box_rect.y + 10))