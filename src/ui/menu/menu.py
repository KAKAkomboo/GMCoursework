import pygame
import random
from src.core.settings import screen_width, screen_height

class AshParticle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()
        # Randomize initial position to fill screen
        self.x = random.randint(0, w)
        self.y = random.randint(0, h)

    def reset(self):
        self.x = random.randint(0, self.w)
        self.y = random.randint(self.h, self.h + 100)
        self.speed = random.uniform(0.5, 2.0)
        self.drift = random.uniform(-0.5, 0.5)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(50, 150)

    def update(self):
        self.y -= self.speed
        self.x += self.drift
        if self.y < -10:
            self.reset()

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((200, 200, 200, self.alpha))
        surface.blit(s, (int(self.x), int(self.y)))

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ["Start Game", "Options", "Quit"]
        self.selected = 0

        try:
            self.font_title = pygame.font.SysFont("timesnewroman", 72, bold=True)
            self.font_option = pygame.font.SysFont("timesnewroman", 36)
        except:
            self.font_title = pygame.font.SysFont(None, 80)
            self.font_option = pygame.font.SysFont(None, 40)

        try:
            img = pygame.image.load("src/assets/images/Background_Images/bggame.png").convert_alpha()
            self.bg_image_original = img
            self.bg_image = pygame.transform.scale(img, (screen.get_width(), screen.get_height()))
        except Exception as e:
            print("Background load failed:", e)
            self.bg_image_original = None
            self.bg_image = None

        self.particles = [AshParticle(screen.get_width(), screen.get_height()) for _ in range(50)]

        self.spacing = 60
        self.recalculate_layout()

    def recalculate_layout(self):
        current_w, current_h = self.screen.get_size()

        if self.bg_image_original:
            self.bg_image = pygame.transform.scale(self.bg_image_original, (current_w, current_h))

        self.particles = [AshParticle(current_w, current_h) for _ in range(50)]

        self.start_y = int(current_h * 0.6)
        self.option_rects = []
        for i, option in enumerate(self.options):
            text = self.font_option.render(option, True, (255, 255, 255))
            rect = text.get_rect(center=(current_w // 2, self.start_y + i * self.spacing))
            self.option_rects.append(rect)

    def draw(self):
        current_w, current_h = self.screen.get_size()

        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((10, 10, 10))

        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)

        for y in range(current_h):
            alpha = int((y / current_h) * 150)
            pygame.draw.line(overlay, (0, 0, 0, alpha), (0, y), (current_w, y))
        self.screen.blit(overlay, (0, 0))

        for p in self.particles:
            p.update()
            p.draw(self.screen)

        title_surf = self.font_title.render("DARK SOULS", True, (200, 200, 200))
        shadow_surf = self.font_title.render("DARK SOULS", True, (0, 0, 0))
        title_rect = title_surf.get_rect(center=(current_w // 2, current_h * 0.25))
        self.screen.blit(shadow_surf, (title_rect.x + 4, title_rect.y + 4))
        self.screen.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for i, option in enumerate(self.options):
            rect = self.option_rects[i]
            is_hovered = rect.collidepoint(mouse_pos)
            is_selected = (i == self.selected)
            
            color = (150, 150, 150)
            if is_selected or is_hovered:
                color = (255, 255, 255)
                indicator_points = [
                    (rect.left - 20, rect.centery),
                    (rect.left - 30, rect.centery - 5),
                    (rect.left - 30, rect.centery + 5)
                ]
                pygame.draw.polygon(self.screen, (200, 50, 50), indicator_points)

                glow_surf = self.font_option.render(option, True, (200, 200, 200))
                glow_surf.set_alpha(50)
                self.screen.blit(glow_surf, (rect.x - 2, rect.y - 2))
                self.screen.blit(glow_surf, (rect.x + 2, rect.y + 2))

            text_surf = self.font_option.render(option, True, color)
            self.screen.blit(text_surf, rect)

    def handle_ev(self, events):
        action = None
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    action = self._get_action(self.selected)
                elif event.key == pygame.K_ESCAPE:
                    action = "quit"

            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected = i

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected = i
                        action = self._get_action(i)
                        break

        return action

    def _get_action(self, index):
        return ["start", "options", "quit"][index]
