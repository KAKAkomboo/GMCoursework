import pygame
import os


class Cutscene:
    def __init__(self, screen, scenes, font_size=32, color=(200, 200, 200), speed=1.5):
        self.screen = screen
        self.scenes = scenes
        self.font = pygame.font.SysFont("timesnewroman", font_size)
        self.color = color
        self.speed = speed

        self.scene_index = 0
        self.char_index = 0.0
        self.is_active = True
        self.is_line_complete = False

        self.images = {}
        self.load_images()

        self.state = "FADING_IN"
        self.fade_alpha = 255
        self.fade_speed = 3

    def load_images(self):
        for i, scene in enumerate(self.scenes):
            path = scene.get("image")
            if path and os.path.exists(path):
                try:
                    self.images[i] = pygame.image.load(path).convert()
                except pygame.error as e:
                    print(f"Failed to load cutscene image: {path}. Error: {e}")
                    self.images[i] = self.create_placeholder(f"Image {i+1} not found")
            else:
                self.images[i] = self.create_placeholder(f"Scene {i+1}")

    def create_placeholder(self, text):
        surf = pygame.Surface(self.screen.get_size())
        surf.fill((10, 10, 10))
        font = pygame.font.SysFont("arial", 40)
        text_surf = font.render(text, True, (50, 50, 50))
        rect = text_surf.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        surf.blit(text_surf, rect)
        return surf

    def handle_event(self, event):
        if self.state != "TEXT_DISPLAY":
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if not self.is_line_complete:
                    self.char_index = len(self.scenes[self.scene_index]["text"])
                else:
                    self.state = "FADING_OUT"

    def next_scene(self):
        if self.scene_index < len(self.scenes) - 1:
            self.scene_index += 1
            self.char_index = 0.0
            self.is_line_complete = False
            self.state = "FADING_IN"
            self.fade_alpha = 255
        else:
            self.is_active = False

    def update(self, dt):
        if not self.is_active:
            return False

        if self.state == "FADING_IN":
            self.fade_alpha -= self.fade_speed * (dt / 16.0)
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.state = "TEXT_DISPLAY"
        elif self.state == "FADING_OUT":
            self.fade_alpha += self.fade_speed * (dt / 16.0)
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.next_scene()
        elif self.state == "TEXT_DISPLAY":
            if self.char_index < len(self.scenes[self.scene_index]["text"]):
                self.char_index += self.speed * (dt / 16.0)
            else:
                self.is_line_complete = True

        return True

    def draw(self):
        if not self.is_active:
            return

        bg_image = self.images.get(self.scene_index)
        if bg_image:
            scaled_bg = pygame.transform.scale(bg_image, self.screen.get_size())
            self.screen.blit(scaled_bg, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        if self.state == "TEXT_DISPLAY":
            current_line_text = self.scenes[self.scene_index]["text"]
            visible_text = current_line_text[:int(self.char_index)]
            self.draw_text_wrapped(visible_text)

            if self.is_line_complete:
                icon_surf = pygame.Surface((10, 10), pygame.SRCALPHA)
                pygame.draw.polygon(icon_surf, (200, 200, 200), [(0, 0), (10, 5), (0, 10)])
                self.screen.blit(icon_surf, (self.screen.get_width() - 40, self.screen.get_height() - 40))

        if self.state in ["FADING_IN", "FADING_OUT"]:
            fade_surface = pygame.Surface(self.screen.get_size())
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))

    def draw_text_wrapped(self, text):
        words = text.split(' ')
        lines = []
        current_line = []
        max_width = self.screen.get_width() * 0.8

        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = self.font.size(test_line)
            if w < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))

        total_height = len(lines) * self.font.get_height()
        start_y = self.screen.get_height() - total_height - 60

        for i, line in enumerate(lines):
            shadow_surf = self.font.render(line, True, (0, 0, 0))
            shadow_rect = shadow_surf.get_rect(center=(self.screen.get_width() // 2 + 2, start_y + i * self.font.get_height() + 2))
            self.screen.blit(shadow_surf, shadow_rect)

            surf = self.font.render(line, True, self.color)
            rect = surf.get_rect(center=(self.screen.get_width() // 2, start_y + i * self.font.get_height()))
            self.screen.blit(surf, rect)
