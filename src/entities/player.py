import pygame
import math
import random
from src.core.settings import tile_size


class Sword(pygame.sprite.Sprite):
    def __init__(self, owner, width=48, height=12, color=(0, 255, 255)):
        super().__init__()
        self.owner = owner
        self.width = width
        self.height = height
        self.color = color

        self.base_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.base_image.fill(self.color)

        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.active = False

    def set_by_angle(self, angle_deg):
        self.image = pygame.transform.rotate(self.base_image, -angle_deg)
        self.rect = self.image.get_rect()

        rad = math.radians(angle_deg)
        orbit_radius = (tile_size // 2) + (self.width // 2)
        offset_x = math.cos(rad) * orbit_radius
        offset_y = math.sin(rad) * orbit_radius

        self.rect.center = (
            int(self.owner.x * tile_size + offset_x),
            int(self.owner.y * tile_size + offset_y)
        )


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, map_instance):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.map = map_instance

        self.image = pygame.Surface((tile_size, tile_size + 32))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(int(self.x * tile_size), int(self.y * tile_size)))

        self.base_speed = 0.4
        self.run_speed = 0.4
        self.sprint_speed = 0.8
        self.speed = self.base_speed
        self.moving = False
        self.target_x = self.x
        self.target_y = self.y

        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.stamina_depletion_rate = 0.2
        self.stamina_recovery_rate = 0.1
        self.sprinting = False

        self.health = 100
        self.max_health = 100
        self.alive = True
        self.show_death_popup = False

        self.death_x = self.x
        self.death_y = self.y

        self.respawn_x = self.x
        self.respawn_y = self.y

        self.weapon_damage = 25
        self.attack_range = 1.5
        self.attacking = False
        self.attack_cooldown = 100
        self.last_attack_time = 0

        self.has_sword = False
        self.sword = Sword(self)
        self.swinging = False
        self.swing_time = 0
        self.swing_duration = 300
        self.swing_start_angle = 0.0
        self.swing_arc_degrees = 180

        self.locked_target = None
        self.lock_pressed_last = False

        self.facing_angle = 0.0

        self.currency = 0

        self.soul_anim_timer = 0


    def handle_movement(self, keys):
        if not self.moving:
            dx, dy = 0, 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            if keys[pygame.K_LSHIFT]:
                if self.stamina > 0:
                    self.speed = self.sprint_speed
                    self.sprinting = True
                    self.stamina -= self.stamina_depletion_rate
                    if self.stamina < 0:
                        self.stamina = 0
                else:
                    self.speed = self.run_speed
                    self.sprinting = False
            else:
                self.sprinting = False
                self.speed = self.run_speed if (dx or dy) else self.base_speed
                if self.stamina < self.max_stamina:
                    self.stamina += self.stamina_recovery_rate
                    if self.stamina > self.max_stamina:
                        self.stamina = self.max_stamina

            if dx or dy:
                new_x = self.x + dx
                new_y = self.y + dy
                if self.map.is_walkable(new_x, new_y) and self.map.is_walkable(new_x, new_y + 1):
                    self.target_x, self.target_y = new_x, new_y
                    self.moving = True

        if self.moving:
            self.move_towards_target()

    def move_towards_target(self):
        if self.x < self.target_x:
            self.x += self.speed
        elif self.x > self.target_x:
            self.x -= self.speed
        if self.y < self.target_y:
            self.y += self.speed
        elif self.y > self.target_y:
            self.y -= self.speed

        if abs(self.x - self.target_x) < self.speed and abs(self.y - self.target_y) < self.speed:
            self.x, self.y = self.target_x, self.target_y
            self.moving = False

    def toggle_lock(self, npc_group):
        if self.locked_target:
            self.locked_target = None
            return

        if npc_group:
            nearest = None
            nearest_dist = float("inf")
            for npc in npc_group:
                if getattr(npc, "alive", True):
                    dist = math.dist((self.x, self.y), getattr(npc, "pos", (npc.rect.centerx / tile_size, npc.rect.centery / tile_size)))
                    if dist < nearest_dist:
                        nearest = npc
                        nearest_dist = dist
            self.locked_target = nearest

    def obtain_sword(self):
        self.has_sword = True
        print("Player obtained a sword!")

    def swing_sword(self):
        if not self.has_sword or self.swinging:
            return
        self.swinging = True
        self.swing_time = 0
        if self.locked_target and getattr(self.locked_target, "alive", True):
            tx, ty = getattr(self.locked_target, "pos", (self.locked_target.rect.centerx / tile_size, self.locked_target.rect.centery / tile_size))
            dx = tx - self.x
            dy = ty - self.y
            aim_angle = math.degrees(math.atan2(dy, dx))
        else:
            aim_angle = self.facing_angle
        self.swing_start_angle = aim_angle - (self.swing_arc_degrees / 2)
        self.sword.active = True
        print("Sword swing started!")

    def update_sword(self, dt_ms, npc_group=None):
        if self.swinging:
            self.swing_time += dt_ms
            progress = max(0.0, min(1.0, self.swing_time / self.swing_duration))
            current_angle = self.swing_start_angle + progress * self.swing_arc_degrees
            self.sword.set_by_angle(current_angle)
            if npc_group:
                for npc in npc_group:
                    if getattr(npc, "alive", True) and self.sword.rect.colliderect(npc.rect):
                        npc.take_damage(self.weapon_damage)
            if progress >= 1.0:
                self.swinging = False
                self.sword.active = False
                print("Sword swing ended.")


    def weapon_attack(self, npc_group):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time < self.attack_cooldown:
            return
        self.last_attack_time = now
        self.attacking = True
        if self.locked_target and getattr(self.locked_target, "alive", True):
            dist = math.dist((self.x, self.y), getattr(self.locked_target, "pos", (self.locked_target.rect.centerx / tile_size, self.locked_target.rect.centery / tile_size)))
            if dist <= self.attack_range:
                tx, ty = getattr(self.locked_target, "pos", (self.locked_target.rect.centerx / tile_size, self.locked_target.rect.centery / tile_size))
                dx = tx - self.x
                dy = ty - self.y
                self.facing_angle = math.degrees(math.atan2(dy, dx))
                self.locked_target.take_damage(self.weapon_damage)
                print(f"Player hit locked NPC for {self.weapon_damage} damage!")
        else:
            for npc in npc_group or []:
                if getattr(npc, "alive", True):
                    dist = math.dist((self.x, self.y), getattr(npc, "pos", (npc.rect.centerx / tile_size, npc.rect.centery / tile_size)))
                    if dist <= self.attack_range:
                        npc.take_damage(self.weapon_damage)
                        print(f"Player hit NPC for {self.weapon_damage} damage!")
                        break

    def shoot(self, shoot_dir_right=True):
        direction = 1 if shoot_dir_right else -1
        print(f"Player shoots {'right' if direction == 1 else 'left'}")

    def add_currency(self, amount):
        if amount > 0:
            self.currency += amount
            print(f"Currency gained: +{amount}. Total: {self.currency}")

    def take_damage(self, damage):
        if self.alive:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.alive = False
                self.show_death_popup = True
                # Record where the player died
                self.death_x, self.death_y = self.x, self.y
                print("Player died!")
        else:
            print(f"Player took {damage} damage!")

    def restart(self):
        self.health = self.max_health
        self.alive = True
        self.show_death_popup = False
        self.x, self.y = self.respawn_x, self.respawn_y
        self.target_x, self.target_y = self.x, self.y
        self.moving = False
        self.locked_target = None
        self.swinging = False
        self.sword.active = False
        self.currency = 0
        self.stamina = self.max_stamina  # reset stamina

    def restore_health_and_flasks(self):
        self.health = self.max_health
        self.stamina = self.max_stamina

    def block_input(self):
        self.moving = False
        self.target_x = self.x
        self.target_y = self.y

    def update(self, keys, npc_group=None, mouse_clicked=False, dt=16.0,
               shoot=False, shoot_dir_right=True, lock_pressed=False,
               attack_pressed=False, obtain_pressed=False):
        if not self.alive:
            return

        if lock_pressed and not self.lock_pressed_last:
            self.toggle_lock(npc_group)
        self.lock_pressed_last = lock_pressed

        if obtain_pressed and not self.has_sword:
            self.obtain_sword()

        self.handle_movement(keys)

        if mouse_clicked:
            self.weapon_attack(npc_group)

        if attack_pressed and not self.swinging:
            self.swing_sord_safe()

        if shoot:
            self.shoot(shoot_dir_right)

        self.rect.center = (int(self.x * tile_size), int(self.y * tile_size))

        self.update_sword(dt, npc_group=npc_group)
        self.soul_anim_timer += 1

    def swing_sord_safe(self):
        self.swing_sword()

    def draw_bar_gradient(self, surface, rect, color_start, color_end):
        x, y, w, h = rect
        if w <= 0: return

        grad_surf = pygame.Surface((w, h))

        for i in range(h):
            ratio = i / h
            r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
            g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
            b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)
            pygame.draw.line(grad_surf, (r, g, b), (0, i), (w, i))
            
        surface.blit(grad_surf, (x, y))

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x * tile_size - camera_x, self.y * tile_size - camera_y))

        if self.has_sword and (self.swinging or self.sword.active):
            screen.blit(self.sword.image, (self.sword.rect.x - camera_x, self.sword.rect.y - camera_y))

        ui_x, ui_y = 30, 30

        max_bar_width = 600
        hp_w = min(int(self.max_health * 3), max_bar_width)
        st_w = min(int(self.max_stamina * 2.4), max_bar_width)
        
        hp_h = 14
        st_h = 10
        st_offset = 20

        col_hp_start = (180, 30, 30)
        col_hp_end = (90, 10, 10)
        col_st_start = (30, 160, 30)
        col_st_end = (10, 70, 10)
        col_border = (165, 140, 80)
        col_bg = (10, 10, 10, 200)

        s_hp = pygame.Surface((hp_w + 4, hp_h + 4), pygame.SRCALPHA)
        s_hp.fill(col_bg)
        screen.blit(s_hp, (ui_x - 2, ui_y - 2))

        hp_ratio = max(0, self.health / self.max_health)
        current_hp_w = int(hp_w * hp_ratio)
        if current_hp_w > 0:
            self.draw_bar_gradient(screen, (ui_x, ui_y, current_hp_w, hp_h), col_hp_start, col_hp_end)

        pygame.draw.rect(screen, col_border, (ui_x - 1, ui_y - 1, hp_w + 2, hp_h + 2), 1)

        st_x, st_y = ui_x, ui_y + st_offset

        s_st = pygame.Surface((st_w + 4, st_h + 4), pygame.SRCALPHA)
        s_st.fill(col_bg)
        screen.blit(s_st, (st_x - 2, st_y - 2))

        st_ratio = max(0, self.stamina / self.max_stamina)
        current_st_w = int(st_w * st_ratio)
        if current_st_w > 0:
            self.draw_bar_gradient(screen, (st_x, st_y, current_st_w, st_h), col_st_start, col_st_end)

        pygame.draw.rect(screen, col_border, (st_x - 1, st_y - 1, st_w + 2, st_h + 2), 1)

        if self.locked_target and getattr(self.locked_target, "alive", True):
            tx, ty = getattr(self.locked_target, "pos", (self.locked_target.rect.centerx / tile_size, self.locked_target.rect.centery / tile_size))
            target_screen_x = int(tx * tile_size - camera_x)
            target_screen_y = int(ty * tile_size - camera_y)
            pygame.draw.circle(screen, (255, 255, 255), (target_screen_x, target_screen_y), 5)

        self.draw_currency(screen)

    def draw_currency(self, screen):
        font = pygame.font.SysFont("timesnewroman", 36)
        text = font.render(f"{self.currency}", True, (255, 255, 255))

        padding_x = 40
        padding_y = 40
        
        pos_x = screen.get_width() - padding_x - text.get_width()
        pos_y = screen.get_height() - padding_y - text.get_height()

        shadow = font.render(f"{self.currency}", True, (0, 0, 0))
        screen.blit(shadow, (pos_x + 2, pos_y + 2))
        screen.blit(text, (pos_x, pos_y))

        icon_x = pos_x - 30
        icon_y = pos_y + text.get_height() // 2

        pulse = (math.sin(self.soul_anim_timer * 0.1) + 1) * 2

        glow_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (100, 200, 255, 50), (20, 20), 15 + pulse)
        screen.blit(glow_surf, (icon_x - 20, icon_y - 20))

        pygame.draw.circle(screen, (200, 240, 255), (icon_x, icon_y), 6)
        pygame.draw.circle(screen, (255, 255, 255), (icon_x, icon_y), 3)
