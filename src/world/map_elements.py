import pygame
from src.core.settings import tile_size


# CHECK POINT

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = int(x)
        self.y = int(y)
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.image.fill((255, 140, 0))
        self.rect = self.image.get_rect(center=(self.x * tile_size, self.y * tile_size))
        self.active = False
        self.menu_open = False
        self.upgrade_open = False
        self.save_cooldown_ms = 1500
        self.last_save_time = 0
        self.prompt_alpha = 255
        self.prompt_dir = -8
        self.save_sound = None
        self.level_sound = None

    def set_sounds(self, save_sound, level_sound):
        self.save_sound = save_sound
        self.level_sound = level_sound

    def is_player_near(self, player):
        return self.rect.colliderect(player.rect)

    def update_active(self, player):
        self.active = self.is_player_near(player)

    def open_menu(self, player):
        self.menu_open = True
        self.upgrade_open = False

    def close_all(self):
        self.menu_open = False
        self.upgrade_open = False

    def try_save(self, player, now_ms, toast):
        if now_ms - self.last_save_time < self.save_cooldown_ms:
            return
        player.death_x = self.x
        player.death_y = self.y
        self.last_save_time = now_ms
        if self.save_sound:
            self.save_sound.play()
        toast.show("Progress saved. Respawn set to this checkpoint.", 1500)

    def open_upgrade(self):
        self.upgrade_open = True

    def draw_bonfire(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x * tile_size - camera_x, self.y * tile_size - camera_y))
        if self.active:
            cx = int(self.x * tile_size - camera_x + self.image.get_width() // 2)
            cy = int(self.y * tile_size - camera_y + self.image.get_height() // 2)
            pygame.draw.circle(screen, (255, 220, 100), (cx, cy), 26, 2)

    def draw_prompt(self, screen, camera_x, camera_y, font_small):
        if not self.active or self.menu_open or self.upgrade_open:
            return
        self.prompt_alpha += self.prompt_dir
        if self.prompt_alpha <= 80 or self.prompt_alpha >= 255:
            self.prompt_dir *= -1
        text = font_small.render("Press E to interact", True, (255, 255, 255))
        s = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        s.fill((0, 0, 0, 120))
        px = int(self.x * tile_size - camera_x + self.image.get_width() // 2 - text.get_width() // 2)
        py = int(self.y * tile_size - camera_y - 50)
        screen.blit(s, (px, py))
        text.set_alpha(self.prompt_alpha)
        screen.blit(text, (px, py))

    def draw_menu(self, screen, font, font_small):
        if not self.menu_open or self.upgrade_open:
            return
        w = screen.get_width()
        h = screen.get_height()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        title = font.render("Checkpoint", True, (255, 255, 255))
        b1 = font.render("Save", True, (0, 0, 0))
        b2 = font.render("Level Up", True, (0, 0, 0))
        hint = font_small.render("Esc or Right Mouse Button to close", True, (220, 220, 220))
        panel_w = 420
        panel_h = 280
        panel_x = w // 2 - panel_w // 2
        panel_y = h // 2 - panel_h // 2
        panel = pygame.Surface((panel_w, panel_h))
        panel.fill((24, 24, 24))
        screen.blit(panel, (panel_x, panel_y))
        screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 20))
        btn_w = 320
        btn_h = 60
        btn1 = pygame.Rect(panel_x + panel_w // 2 - btn_w // 2, panel_y + 90, btn_w, btn_h)
        btn2 = pygame.Rect(panel_x + panel_w // 2 - btn_w // 2, panel_y + 170, btn_w, btn_h)
        pygame.draw.rect(screen, (255, 232, 102), btn1, 0, 8)
        pygame.draw.rect(screen, (144, 238, 144), btn2, 0, 8)
        screen.blit(b1, (btn1.centerx - b1.get_width() // 2, btn1.centery - b1.get_height() // 2))
        screen.blit(b2, (btn2.centerx - b2.get_width() // 2, btn2.centery - b2.get_height() // 2))
        screen.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2, panel_y + panel_h - 35))
        return btn1, btn2

    def handle_menu_mouse(self, player, toast, btns, now_ms):
        if not btns:
            return
        btn1, btn2 = btns
        mx, my = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()
        if pressed[0]:
            if btn1.collidepoint(mx, my):
                self.try_save(player, now_ms, toast)
                self.menu_open = False
            elif btn2.collidepoint(mx, my):
                self.upgrade_open = True

    def handle_menu_keys(self, player, keys, now_ms, toast):
        if keys[pygame.K_1]:
            self.try_save(player, now_ms, toast)
            self.menu_open = False
        elif keys[pygame.K_2]:
            self.upgrade_open = True
        elif keys[pygame.K_ESCAPE]:
            self.menu_open = False

    def draw(self, screen, camera_x, camera_y, font, font_small):
        self.draw_bonfire(screen, camera_x, camera_y)
        self.draw_prompt(screen, camera_x, camera_y, font_small)
        if self.menu_open and not self.upgrade_open:
            return self.draw_menu(screen, font, font_small)
        return None
