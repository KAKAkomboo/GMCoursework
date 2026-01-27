import pygame
import random
from src.core.settings import tile_size

class Checkpoint(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = int(x)
        self.y = int(y)
        self.image = pygame.Surface((tile_size * 2, tile_size * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x * tile_size + tile_size / 2, self.y * tile_size + tile_size / 2))
        

        self.fire_particles = []
        self.bonfire_lit = False
        self.base_color = (40, 40, 40)
        self.base_radius = tile_size // 2

        self.active = False
        self.menu_open = False
        self.upgrade_open = False

        self.interact_cooldown_ms = 500
        self.last_interact_time = 0
        self.prompt_alpha = 255
        self.prompt_dir = -8

        self.save_sound = None
        self.level_sound = None

    def set_sounds(self, save_sound, level_sound):
        self.save_sound = save_sound
        self.level_sound = level_sound

    def is_player_near(self, player):
        return self.rect.colliderect(player.rect.inflate(tile_size, tile_size))

    def update(self, player, now_ms):
        self.update_active(player)
        self.update_fire_particles()
        if self.menu_open:
            player.block_input()

    def update_active(self, player):
        self.active = self.is_player_near(player)

    def update_fire_particles(self):
        # Add new particles
        if self.bonfire_lit:
            if len(self.fire_particles) < 50: # Max particles
                self.fire_particles.append(self.create_particle())

        for particle in self.fire_particles:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.fire_particles.remove(particle)

    def create_particle(self):
        pos = [self.rect.centerx, self.rect.centery]
        vel = [random.uniform(-0.5, 0.5), random.uniform(-1, -0.2)]
        color = random.choice([(255, 140, 0), (255, 80, 0), (255, 180, 0)])
        life = random.randint(20, 40)
        return {'pos': pos, 'vel': vel, 'life': life, 'color': color}

    def open_menu(self, player):
        self.menu_open = True
        self.upgrade_open = False

    def close_all(self):
        self.menu_open = False
        self.upgrade_open = False

    def rest(self, player, toast, world):
        if not self.bonfire_lit:
            self.bonfire_lit = True
            toast.show("Bonfire Lit", 2000)

        player.respawn_x = self.x
        player.respawn_y = self.y

        if hasattr(player, 'restore_health_and_flasks'):
            player.restore_health_and_flasks()

        if world:
            world.respawn_enemies()
        
        if self.save_sound:
            self.save_sound.play()
            
        toast.show("Rested. Enemies have respawned.", 2000)
        self.close_all()

    def open_upgrade(self):
        self.upgrade_open = True

    def draw(self, screen, camera_x, camera_y, font, font_small):
        base_pos = (self.rect.centerx - camera_x, self.rect.centery - camera_y)
        pygame.draw.circle(screen, self.base_color, base_pos, self.base_radius)

        for particle in self.fire_particles:
            pos = (int(particle['pos'][0] - camera_x), int(particle['pos'][1] - camera_y))
            pygame.draw.circle(screen, particle['color'], pos, int(particle['life'] / 4))

        self.draw_prompt(screen, camera_x, camera_y, font_small)
        
        if self.menu_open and not self.upgrade_open:
            return self.draw_menu(screen, font, font_small)
        return None

    def draw_prompt(self, screen, camera_x, camera_y, font_small):
        if not self.active or self.menu_open or self.upgrade_open:
            return
            
        self.prompt_alpha += self.prompt_dir
        if self.prompt_alpha <= 80 or self.prompt_alpha >= 255:
            self.prompt_dir *= -1
            
        prompt_text = "Light Bonfire" if not self.bonfire_lit else "Rest at Bonfire"
        text = font_small.render(f"Press E to {prompt_text}", True, (255, 255, 255))
        s = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        s.fill((0, 0, 0, 120))
        
        px = int(self.rect.centerx - camera_x - text.get_width() // 2)
        py = int(self.rect.top - camera_y - 30)
        
        screen.blit(s, (px, py))
        text.set_alpha(self.prompt_alpha)
        screen.blit(text, (px, py))

    def draw_menu(self, screen, font, font_small):
        if not self.menu_open or self.upgrade_open:
            return
            
        w, h = screen.get_width(), screen.get_height()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        title_text = "Bonfire"
        b1_text = "Rest"
        b2_text = "Level Up"
        
        title = font.render(title_text, True, (255, 255, 255))
        b1 = font.render(b1_text, True, (0, 0, 0))
        b2 = font.render(b2_text, True, (0, 0, 0))
        hint = font_small.render("Esc or Right Mouse Button to close", True, (220, 220, 220))
        
        panel_w, panel_h = 420, 280
        panel_x, panel_y = w // 2 - panel_w // 2, h // 2 - panel_h // 2
        
        panel = pygame.Surface((panel_w, panel_h))
        panel.fill((24, 24, 24))
        screen.blit(panel, (panel_x, panel_y))
        screen.blit(title, (panel_x + panel_w // 2 - title.get_width() // 2, panel_y + 20))
        
        btn_w, btn_h = 320, 60
        btn1 = pygame.Rect(panel_x + panel_w // 2 - btn_w // 2, panel_y + 90, btn_w, btn_h)
        btn2 = pygame.Rect(panel_x + panel_w // 2 - btn_w // 2, panel_y + 170, btn_w, btn_h)
        
        pygame.draw.rect(screen, (255, 165, 0), btn1, 0, 8) # Orange for Rest
        pygame.draw.rect(screen, (144, 238, 144), btn2, 0, 8) # Green for Level Up
        
        screen.blit(b1, (btn1.centerx - b1.get_width() // 2, btn1.centery - b1.get_height() // 2))
        screen.blit(b2, (btn2.centerx - b2.get_width() // 2, btn2.centery - b2.get_height() // 2))
        screen.blit(hint, (panel_x + panel_w // 2 - hint.get_width() // 2, panel_y + panel_h - 35))
        
        return btn1, btn2

    def handle_menu_mouse(self, player, toast, world, btns, now_ms):
        if not btns or pygame.time.get_ticks() - self.last_interact_time < self.interact_cooldown_ms:
            return
            
        btn1, btn2 = btns
        mx, my = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()
        
        if pressed[0]:
            self.last_interact_time = now_ms
            if btn1.collidepoint(mx, my):
                self.rest(player, toast, world)
            elif btn2.collidepoint(mx, my):
                if self.level_sound:
                    self.level_sound.play()
                self.open_upgrade()

    def handle_menu_keys(self, player, toast, world, keys, now_ms):
        if pygame.time.get_ticks() - self.last_interact_time < self.interact_cooldown_ms:
            return

        if keys[pygame.K_1]:
            self.last_interact_time = now_ms
            self.rest(player, toast, world)
        elif keys[pygame.K_2]:
            self.last_interact_time = now_ms
            if self.level_sound:
                self.level_sound.play()
            self.open_upgrade()
        elif keys[pygame.K_ESCAPE]:
            self.last_interact_time = now_ms
            self.close_all()
