import pygame

class DeathScreen:
    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height

        try:
            self.font_large = pygame.font.SysFont("timesnewroman", 90, bold=True)
            self.font_small = pygame.font.SysFont("timesnewroman", 30)
        except:
            self.font_large = pygame.font.SysFont(None, 100)
            self.font_small = pygame.font.SysFont(None, 30)

        self.active = False
        self.anim_timer = 0
        self.bg_alpha = 0
        self.text_alpha = 0
        self.restart_alpha = 0

        self.text_surf = self.font_large.render("YOU DIED", True, (180, 20, 20)) # Dark Red
        self.text_rect = self.text_surf.get_rect(center=(self.w // 2, self.h // 2))

        self.restart_surf = self.font_small.render("Press R to Restart", True, (200, 200, 200))
        self.restart_rect = self.restart_surf.get_rect(center=(self.w // 2, self.h // 2 + 80))

    def show(self):
        if not self.active:
            self.active = True
            self.anim_timer = 0
            self.bg_alpha = 0
            self.text_alpha = 0
            self.restart_alpha = 0

    def hide(self):
        self.active = False

    def update(self):
        if not self.active:
            return

        self.anim_timer += 1

        if self.bg_alpha < 180:
            self.bg_alpha += 3

        if self.anim_timer > 30:
            if self.text_alpha < 255:
                self.text_alpha += 2

        if self.anim_timer > 180:
            if self.restart_alpha < 255:
                self.restart_alpha += 5

    def draw(self, screen):
        if not self.active:
            return

        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, int(self.bg_alpha)))
        screen.blit(overlay, (0, 0))

        if self.text_alpha > 0:
            temp_surf = self.text_surf.copy()
            temp_surf.set_alpha(int(self.text_alpha))

            shadow_surf = self.font_large.render("YOU DIED", True, (0, 0, 0))
            shadow_surf.set_alpha(int(self.text_alpha * 0.8))
            screen.blit(shadow_surf, (self.text_rect.x + 4, self.text_rect.y + 4))

            screen.blit(temp_surf, self.text_rect)

            if self.text_alpha > 50:
                line_w = int(self.w * (self.text_alpha / 255.0))
                line_h = 2
                line_surf = pygame.Surface((line_w, line_h), pygame.SRCALPHA)
                line_surf.fill((100, 0, 0, int(self.text_alpha * 0.5)))
                line_rect = line_surf.get_rect(center=(self.w // 2, self.h // 2))
                screen.blit(line_surf, line_rect)

        if self.restart_alpha > 0:
            temp_restart = self.restart_surf.copy()
            temp_restart.set_alpha(int(self.restart_alpha))
            screen.blit(temp_restart, self.restart_rect)
