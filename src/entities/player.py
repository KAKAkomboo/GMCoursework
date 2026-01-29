import pygame
import math
import random
from src.core.settings import tile_size

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, damage):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 150), (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.pos = pygame.math.Vector2(x, y)
        self.vel = direction * 12.0 # Speed
        self.damage = damage
        self.life_time = 60

    def update(self):
        self.pos += self.vel
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        self.life_time -= 1
        if self.life_time <= 0:
            self.kill()

class Weapon(pygame.sprite.Sprite):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner
        self.mode = "saw_cleaver_normal"

        self.modes = {
            "saw_cleaver_normal": {
                "damage": 15,
                "range": 45,
                "arc": 120,
                "color": (180, 180, 180),
                "width": 10,
                "length": 40,
                "stamina_cost": 15,
                "startup": 100,
                "active": 100,
                "recovery": 200,
                "shake": 2,
                "hit_stop": 50
            },
            "saw_cleaver_extended": {
                "damage": 35,
                "range": 80,
                "arc": 160,
                "color": (100, 50, 50),
                "width": 14,
                "length": 75,
                "stamina_cost": 35,
                "startup": 300,
                "active": 150,
                "recovery": 400,
                "shake": 8,
                "hit_stop": 120
            }
        }
        
        self.image = pygame.Surface((40, 10), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.update_attributes()

    def update_attributes(self):
        stats = self.modes[self.mode]
        self.damage = stats["damage"]
        self.range = stats["range"]
        self.arc = stats["arc"]
        self.color = stats["color"]
        self.stamina_cost = stats["stamina_cost"]
        self.startup_time = stats["startup"]
        self.active_time = stats["active"]
        self.recovery_time = stats["recovery"]
        self.shake_strength = stats["shake"]
        self.hit_stop_duration = stats["hit_stop"]
        
        self.base_image = pygame.Surface((stats["length"], stats["width"]), pygame.SRCALPHA)
        pygame.draw.rect(self.base_image, self.color, (0, 0, stats["length"], stats["width"]), border_radius=2)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()

    def transform(self):
        if self.mode == "saw_cleaver_normal":
            self.mode = "saw_cleaver_extended"
        else:
            self.mode = "saw_cleaver_normal"
        self.update_attributes()

    def update_visual(self, angle):
        self.image = pygame.transform.rotate(self.base_image, -angle)
        self.rect = self.image.get_rect(center=self.owner.rect.center)
        offset = tile_size // 2
        rad = math.radians(angle)
        self.rect.centerx += math.cos(rad) * offset
        self.rect.centery += math.sin(rad) * offset

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, map_instance):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.map = map_instance
        self.game_instance = None

        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 255, 255), (0, 0, tile_size, tile_size), border_radius=5) 
        pygame.draw.rect(self.image, (200, 255, 255), (4, 4, tile_size-8, tile_size-8), border_radius=3)
        self.rect = self.image.get_rect(center=(int(self.x * tile_size), int(self.y * tile_size)))

        self.state = "IDLE"
        self.facing_angle = 0.0


        self.max_health = 100
        self.health = 100
        self.potential_health = 100
        self.ghost_health = 100
        self.rally_timer = 0
        self.rally_window = 3000
        self.rally_decay_speed = 0.2
        self.rally_heal_amount = 12

        self.max_stamina = 100
        self.stamina = 100
        self.stamina_regen = 0.5
        self.stamina_regen_delay = 0

        self.strength = 10
        self.dexterity = 10
        self.blood_shade = 5
        self.sacrament = 5

        self.base_speed = 0.45
        self.dash_speed = 1.5
        self.dash_cost = 20
        self.dash_duration = 200
        self.dash_timer = 0
        self.dash_cooldown = 500
        self.last_dash = 0
        self.dash_progress = 0

        self.weapon = Weapon(self)
        self.attack_timer = 0
        self.attack_phase = "NONE"
        self.attack_start_angle = 0
        self.has_hit_target = False

        self.combo_count = 0
        self.max_combo = 3
        self.combo_window = 400
        self.last_attack_end = 0

        self.bullets = 20
        self.gun_cooldown = 800
        self.last_shot = 0
        self.gun_kickback = 0.5
        self.gun_damage = 10
        self.projectiles = pygame.sprite.Group()

        self.alive = True
        self.death_x = self.x
        self.death_y = self.y
        self.respawn_x = self.x
        self.respawn_y = self.y
        
        self.currency = 0
        self.locked_target = None
        self.soul_anim_timer = 0

    def input(self, keys, mouse_buttons):
        if self.state in ["STUNNED", "VISCERAL"]:
            return

        if self.state == "ATTACK":
            if self.attack_phase == "RECOVERY":
                if keys[pygame.K_SPACE] and self.stamina >= self.dash_cost:
                    self.start_dash()
                elif mouse_buttons[0] and self.stamina >= self.weapon.stamina_cost:
                    if self.combo_count < self.max_combo:
                        self.start_attack(combo=True)
            return

        if self.state == "DASH":
            return

        now = pygame.time.get_ticks()
        dx, dy = 0, 0

        if keys[pygame.K_w]: dy = -1
        if keys[pygame.K_s]: dy = 1
        if keys[pygame.K_a]: dx = -1
        if keys[pygame.K_d]: dx = 1

        if dx != 0 or dy != 0:
            self.facing_angle = math.degrees(math.atan2(dy, dx))
            self.state = "MOVE"
        else:
            self.state = "IDLE"

        if keys[pygame.K_SPACE] and self.stamina >= self.dash_cost:
            if now - self.last_dash > self.dash_cooldown:
                self.start_dash()
                return

        if mouse_buttons[0] and self.stamina >= self.weapon.stamina_cost:
            if now - self.last_attack_end < self.combo_window and self.combo_count < self.max_combo and self.combo_count > 0:
                self.start_attack(combo=True)
            else:
                self.start_attack(combo=False)
            return

        if keys[pygame.K_q]:
            self.shoot_gun(now)

        if keys[pygame.K_f]:
            self.weapon.transform()

        self.move(dx, dy)

    def start_dash(self):
        self.state = "DASH"
        self.dash_timer = pygame.time.get_ticks()
        self.last_dash = self.dash_timer
        self.stamina -= self.dash_cost
        self.stamina_regen_delay = 1000
        self.combo_count = 0 # Dash breaks combo
        self.dash_progress = 0 # Reset progress

    def start_attack(self, combo=False):
        self.state = "ATTACK"
        self.attack_timer = 0
        self.attack_phase = "STARTUP"
        self.has_hit_target = False
        self.stamina -= self.weapon.stamina_cost
        self.stamina_regen_delay = 800
        
        if combo:
            self.combo_count += 1
        else:
            self.combo_count = 1

        mx, my = pygame.mouse.get_pos()
        screen_center_x = pygame.display.get_surface().get_width() // 2
        screen_center_y = pygame.display.get_surface().get_height() // 2
        rel_x = mx - screen_center_x
        rel_y = my - screen_center_y
        self.facing_angle = math.degrees(math.atan2(rel_y, rel_x))

        direction = 1 if self.combo_count % 2 != 0 else -1
        self.attack_start_angle = self.facing_angle - (self.weapon.arc / 2) * direction
        self.attack_direction = direction

    def move(self, dx, dy):
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
        new_x = self.x + dx * self.base_speed
        new_y = self.y + dy * self.base_speed
        if self.map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def update(self, keys, npc_group, mouse_clicked, dt):
        if not self.alive: return
        now = pygame.time.get_ticks()
        mouse_buttons = pygame.mouse.get_pressed()

        if self.state == "DASH":
            self.update_dash(dt)
        elif self.state == "ATTACK":
            self.update_attack(dt, npc_group)
        elif self.state == "VISCERAL":
            self.update_visceral(dt)
        else:
            self.input(keys, mouse_buttons)

        self.update_stamina(dt)
        self.update_rally(dt)
        self.projectiles.update()
        self.check_bullet_collisions(npc_group)
        self.rect.center = (int(self.x * tile_size), int(self.y * tile_size))
        self.soul_anim_timer += 1

    def update_dash(self, dt):
        self.dash_progress += dt
        if self.dash_progress < self.dash_duration:
            rad = math.radians(self.facing_angle)
            dx = math.cos(rad) * self.dash_speed * (dt / 16.0)
            dy = math.sin(rad) * self.dash_speed * (dt / 16.0)
            new_x = self.x + dx
            new_y = self.y + dy
            if self.map.is_walkable(new_x, new_y):
                self.x = new_x
                self.y = new_y
        else:
            self.state = "IDLE"

    def update_attack(self, dt, npc_group):
        self.attack_timer += dt
        startup = self.weapon.startup_time
        active = self.weapon.active_time
        recovery = self.weapon.recovery_time
        
        if self.attack_timer < startup:
            self.attack_phase = "STARTUP"
            self.weapon.update_visual(self.attack_start_angle)
        elif self.attack_timer < startup + active:
            self.attack_phase = "ACTIVE"
            progress = (self.attack_timer - startup) / active
            # Swing arc based on direction
            arc = self.weapon.arc * self.attack_direction
            current_angle = self.attack_start_angle + (arc * progress)
            self.weapon.update_visual(current_angle)
            if not self.has_hit_target:
                self.check_hit(npc_group)
        elif self.attack_timer < startup + active + recovery:
            self.attack_phase = "RECOVERY"
            end_angle = self.attack_start_angle + (self.weapon.arc * self.attack_direction)
            self.weapon.update_visual(end_angle)
        else:
            self.state = "IDLE"
            self.attack_phase = "NONE"
            self.last_attack_end = pygame.time.get_ticks()

    def update_visceral(self, dt):
        self.attack_timer += dt
        if self.attack_timer > 1000:
            self.state = "IDLE"

    def check_hit(self, npc_group):
        if not npc_group: return
        hit_poly = self.weapon.rect
        for npc in npc_group:
            if not getattr(npc, "alive", True): continue
            if hit_poly.colliderect(npc.rect):
                if getattr(npc, "invincible", False): continue
                
                self.has_hit_target = True

                is_open = getattr(npc, "open_for_visceral", False)
                
                if is_open and self.state != "VISCERAL":
                    dist = math.dist((self.x, self.y), getattr(npc, "pos", (0,0)))
                    if dist < 1.5:
                        self.perform_visceral(npc)
                        return

                damage = self.weapon.damage
                if self.combo_count == 2: damage *= 1.2
                elif self.combo_count == 3: damage *= 1.5
                
                npc.take_damage(damage)
                npc.invincible = True 

                if hasattr(npc, "trigger_stagger"):
                    npc.trigger_stagger(300)
                
                self.apply_rally()
                
                if self.game_instance:
                    self.game_instance.trigger_hit_stop(self.weapon.hit_stop_duration)
                    self.game_instance.trigger_screen_shake(200, self.weapon.shake_strength)
                    # Spawn Blood
                    self.game_instance.spawn_blood(npc.rect.centerx, npc.rect.centery, 10)

    def check_bullet_collisions(self, npc_group):
        if not npc_group: return
        hits = pygame.sprite.groupcollide(self.projectiles, npc_group, True, False)
        for bullet, npcs in hits.items():
            for npc in npcs:
                if getattr(npc, "alive", True):
                    npc.take_damage(self.gun_damage)

                    if hasattr(npc, "check_parry_window"):
                        if npc.check_parry_window():
                            print("PARRY SUCCESSFUL!")
                            if hasattr(npc, "trigger_open_for_visceral"):
                                npc.trigger_open_for_visceral()
                            
                            if self.game_instance:
                                self.game_instance.trigger_hit_stop(150, 0.0)
                                self.game_instance.trigger_screen_shake(200, 8)

    def perform_visceral(self, npc):
        self.state = "VISCERAL"
        self.attack_timer = 0
        damage = self.weapon.damage * 6
        npc.take_damage(damage)
        if hasattr(npc, "reset_state"): npc.reset_state()
        
        self.apply_rally(full=True)
        if self.game_instance:
            self.game_instance.trigger_hit_stop(400, 0.0)
            self.game_instance.trigger_screen_shake(500, 20)
            self.game_instance.spawn_blood(npc.rect.centerx, npc.rect.centery, 30)

    def shoot_gun(self, now):
        if now - self.last_shot > self.gun_cooldown:
            if self.bullets > 0:
                self.bullets -= 1
                self.last_shot = now

                mx, my = pygame.mouse.get_pos()
                screen_center_x = pygame.display.get_surface().get_width() // 2
                screen_center_y = pygame.display.get_surface().get_height() // 2

                direction = pygame.math.Vector2(mx - screen_center_x, my - screen_center_y)
                if direction.length() > 0:
                    direction = direction.normalize()
                else:
                    direction = pygame.math.Vector2(1, 0)

                start_x = self.x * tile_size
                start_y = self.y * tile_size
                
                bullet = Bullet(start_x, start_y, direction, self.gun_damage)
                self.projectiles.add(bullet)
                
                if self.game_instance:
                    self.game_instance.trigger_screen_shake(100, 3)
            else:
                print("Click! No ammo.")

    def take_damage(self, amount):
        if self.state == "DASH": return
        self.health -= amount
        self.rally_timer = self.rally_window
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.death_x, self.death_y = self.x, self.y

    def update_rally(self, dt):
        if self.ghost_health > self.health:
            self.ghost_health -= self.rally_decay_speed * dt * 0.5
            if self.ghost_health < self.health: self.ghost_health = self.health
        elif self.ghost_health < self.health: self.ghost_health = self.health

        if self.rally_timer > 0:
            self.rally_timer -= dt
        else:
            if self.potential_health > self.health:
                self.potential_health -= self.rally_decay_speed * dt
                if self.potential_health < self.health: self.potential_health = self.health
        if self.potential_health < self.health: self.potential_health = self.health

    def apply_rally(self, full=False):
        if full: self.health = self.potential_health
        else:
            heal = self.rally_heal_amount
            if self.health < self.potential_health:
                self.health = min(self.potential_health, self.health + heal)

    def update_stamina(self, dt):
        if self.stamina_regen_delay > 0:
            self.stamina_regen_delay -= dt
        elif self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen * (dt / 16.0))

    def draw(self, screen, cam_x, cam_y):
        screen.blit(self.image, (self.x * tile_size - cam_x, self.y * tile_size - cam_y))
        if self.state == "ATTACK":
            screen.blit(self.weapon.image, (self.weapon.rect.x - cam_x, self.weapon.rect.y - cam_y))
        for bullet in self.projectiles:
            screen.blit(bullet.image, (bullet.rect.x - cam_x, bullet.rect.y - cam_y))
        self.draw_hud(screen)

    def draw_hud(self, screen):
        start_x = 80
        start_y = 40

        max_bar_w = 400
        hp_w = min(int(self.max_health * 2.5), max_bar_w)
        st_w = min(int(self.max_stamina * 2.0), max_bar_w)
        hp_h = 12
        st_h = 8

        pygame.draw.rect(screen, (40, 40, 40), (start_x, start_y, hp_w, hp_h))

        ghost_ratio = self.ghost_health / self.max_health
        pygame.draw.rect(screen, (200, 200, 200), (start_x, start_y, int(hp_w * ghost_ratio), hp_h))

        pot_ratio = self.potential_health / self.max_health
        pygame.draw.rect(screen, (200, 100, 0), (start_x, start_y, int(hp_w * pot_ratio), hp_h))

        hp_ratio = self.health / self.max_health
        curr_hp_w = int(hp_w * hp_ratio)
        if curr_hp_w > 0:
            pygame.draw.rect(screen, (180, 20, 20), (start_x, start_y, curr_hp_w, hp_h))

        st_y_pos = start_y + hp_h + 5
        pygame.draw.rect(screen, (40, 40, 40), (start_x, st_y_pos, st_w, st_h))
        st_ratio = self.stamina / self.max_stamina
        curr_st_w = int(st_w * st_ratio)
        if curr_st_w > 0:
            pygame.draw.rect(screen, (40, 160, 40), (start_x, st_y_pos, curr_st_w, st_h))

        vial_x = start_x - 30
        vial_y = start_y + 5
        pygame.draw.circle(screen, (150, 0, 0), (vial_x, vial_y), 12)
        pygame.draw.circle(screen, (50, 0, 0), (vial_x, vial_y), 12, 2)

        bullet_x = start_x - 30
        bullet_y = vial_y + 30
        pygame.draw.circle(screen, (180, 180, 180), (bullet_x, bullet_y), 10)

        font_sm = pygame.font.SysFont("timesnewroman", 20)
        b_txt = font_sm.render(f"{self.bullets}", True, (255, 255, 255))
        screen.blit(b_txt, (bullet_x + 15, bullet_y - 10))


        self.draw_currency(screen)

    def draw_currency(self, screen):
        font = pygame.font.SysFont("timesnewroman", 32)
        text = font.render(f"{self.currency}", True, (255, 255, 255))
        
        padding_x = 30
        padding_y = 30
        
        pos_x = screen.get_width() - padding_x - text.get_width()
        pos_y = padding_y # Top Right
        
        # Icon (Echo symbol)
        icon_x = pos_x - 30
        icon_y = pos_y + text.get_height() // 2
        pygame.draw.circle(screen, (200, 200, 255), (icon_x, icon_y), 8)
        pygame.draw.circle(screen, (255, 255, 255), (icon_x, icon_y), 4)

        shadow = font.render(f"{self.currency}", True, (0, 0, 0))
        screen.blit(shadow, (pos_x + 2, pos_y + 2))
        screen.blit(text, (pos_x, pos_y))

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

    def restore_health_and_flasks(self):
        self.health = self.max_health
        self.potential_health = self.max_health
        self.ghost_health = self.max_health
        self.stamina = self.max_stamina
        self.bullets = 20

    def restart(self):
        self.restore_health_and_flasks()
        self.alive = True
        self.x, self.y = self.respawn_x, self.respawn_y
        self.state = "IDLE"
        self.projectiles.empty()

    def block_input(self):
        self.moving = False
        self.target_x = self.x
        self.target_y = self.y
        self.state = "IDLE"

    def add_currency(self, amount):
        if amount > 0:
            self.currency += amount
            print(f"Currency gained: +{amount}. Total: {self.currency}")
