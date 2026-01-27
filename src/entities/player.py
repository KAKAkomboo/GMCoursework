import pygame
import math
from src.core.settings import tile_size

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, damage):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 255, 150), (4, 4), 4)
        self.rect = self.image.get_rect(center=(x, y))
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.speed = 12.0
        self.damage = damage
        self.angle = angle
        
        rad = math.radians(angle)
        self.vx = math.cos(rad) * self.speed
        self.vy = math.sin(rad) * self.speed
        
        self.life_time = 60 # Frames to live

    def update(self):
        self.pos_x += self.vx
        self.pos_y += self.vy
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
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
                # Phases (Slower)
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
        self.total_duration = self.startup_time + self.active_time + self.recovery_time
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
        self.game_instance = None # Set by Game engine

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

        self.base_speed = 0.45
        self.dash_speed = 1.5
        self.dash_cost = 20
        self.dash_duration = 200
        self.dash_timer = 0
        self.dash_cooldown = 500
        self.last_dash = 0

        self.weapon = Weapon(self)
        self.attack_timer = 0
        self.attack_phase = "NONE"
        self.attack_start_angle = 0
        self.has_hit_target = False

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

    def input(self, keys, mouse_buttons):
        if self.state in ["STUNNED", "VISCERAL"]:
            return

        if self.state == "ATTACK":
            if self.attack_phase == "RECOVERY":
                if keys[pygame.K_SPACE] and self.stamina >= self.dash_cost:
                    self.start_dash()
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
            self.start_attack()
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

    def start_attack(self):
        self.state = "ATTACK"
        self.attack_timer = 0
        self.attack_phase = "STARTUP"
        self.has_hit_target = False
        self.stamina -= self.weapon.stamina_cost
        self.stamina_regen_delay = 800

        mx, my = pygame.mouse.get_pos()
        screen_center_x = pygame.display.get_surface().get_width() // 2
        screen_center_y = pygame.display.get_surface().get_height() // 2
        rel_x = mx - screen_center_x
        rel_y = my - screen_center_y
        self.facing_angle = math.degrees(math.atan2(rel_y, rel_x))
        self.attack_start_angle = self.facing_angle - (self.weapon.arc / 2)

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

    def update_dash(self, dt):
        self.dash_progress += dt
        if self.dash_progress < self.dash_duration:
            rad = math.radians(self.facing_angle)
            dx = math.cos(rad) * self.dash_speed * (dt / 16.0) # Normalize speed to frame
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
            current_angle = self.attack_start_angle + (self.weapon.arc * progress)
            self.weapon.update_visual(current_angle)

            if not self.has_hit_target:
                self.check_hit(npc_group)
                
        elif self.attack_timer < startup + active + recovery:
            self.attack_phase = "RECOVERY"
            end_angle = self.attack_start_angle + self.weapon.arc
            self.weapon.update_visual(end_angle)
            
        else:
            self.state = "IDLE"
            self.attack_phase = "NONE"

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
                
                is_staggered = getattr(npc, "staggered", False)
                
                if is_staggered and self.state != "VISCERAL":
                    self.perform_visceral(npc)
                    return

                damage = self.weapon.damage
                npc.take_damage(damage)
                npc.invincible = True 
                
                self.apply_rally()

                if self.game_instance:
                    self.game_instance.trigger_hit_stop(self.weapon.hit_stop_duration)
                    self.game_instance.trigger_screen_shake(200, self.weapon.shake_strength)

    def check_bullet_collisions(self, npc_group):
        if not npc_group: return

        hits = pygame.sprite.groupcollide(self.projectiles, npc_group, True, False)
        
        for bullet, npcs in hits.items():
            for npc in npcs:
                if getattr(npc, "alive", True):
                    npc.take_damage(self.gun_damage)

                    if getattr(npc, "attacking", False):
                        print("PARRY SUCCESSFUL!")
                        npc.staggered = True
                        npc.stagger_time = pygame.time.get_ticks()
                        npc.attacking = False

                        if self.game_instance:
                            self.game_instance.trigger_hit_stop(100, 0.0) # Freeze frame
                            self.game_instance.trigger_screen_shake(150, 5)

    def perform_visceral(self, npc):
        self.state = "VISCERAL"
        self.attack_timer = 0
        damage = self.weapon.damage * 5
        npc.take_damage(damage)
        npc.staggered = False
        self.apply_rally(full=True)

        if self.game_instance:
            self.game_instance.trigger_hit_stop(300, 0.0) # Full freeze
            self.game_instance.trigger_screen_shake(400, 15)

    def shoot_gun(self, now):
        if now - self.last_shot < self.gun_cooldown and self.bullets > 0:
            return
        
        self.bullets -= 1
        self.last_shot = now

        mx, my = pygame.mouse.get_pos()
        screen_center_x = pygame.display.get_surface().get_width() // 2
        screen_center_y = pygame.display.get_surface().get_height() // 2
        rel_x = mx - screen_center_x
        rel_y = my - screen_center_y
        angle = math.degrees(math.atan2(rel_y, rel_x))

        start_x = self.x * tile_size
        start_y = self.y * tile_size
        bullet = Bullet(start_x, start_y, angle, self.gun_damage)
        self.projectiles.add(bullet)

        rad = math.radians(angle + 180) # Opposite direction
        self.x += math.cos(rad) * self.gun_kickback
        self.y += math.sin(rad) * self.gun_kickback

        if self.game_instance:
            self.game_instance.trigger_screen_shake(100, 3)

    def take_damage(self, amount):
        if self.state == "DASH":
            return

        self.health -= amount
        self.rally_timer = self.rally_window
        
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.death_x, self.death_y = self.x, self.y

    def update_rally(self, dt):
        if self.ghost_health > self.health:
            self.ghost_health -= self.rally_decay_speed * dt * 0.5 # Slow drop
            if self.ghost_health < self.health:
                self.ghost_health = self.health
        elif self.ghost_health < self.health:
             self.ghost_health = self.health
        if self.rally_timer > 0:
            self.rally_timer -= dt
        else:
            if self.potential_health > self.health:
                self.potential_health -= self.rally_decay_speed * dt
                if self.potential_health < self.health:
                    self.potential_health = self.health
        
        if self.potential_health < self.health:
            self.potential_health = self.health

    def apply_rally(self, full=False):
        if full:
            self.health = self.potential_health
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
        bar_x, bar_y = 40, 40
        bar_w, bar_h = 300, 15

        pygame.draw.rect(screen, (20, 20, 20), (bar_x, bar_y, bar_w, bar_h))

        ghost_ratio = self.ghost_health / self.max_health
        pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, int(bar_w * ghost_ratio), bar_h))

        pot_ratio = self.potential_health / self.max_health
        pygame.draw.rect(screen, (180, 100, 0), (bar_x, bar_y, int(bar_w * pot_ratio), bar_h))

        hp_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (180, 20, 20), (bar_x, bar_y, int(bar_w * hp_ratio), bar_h))

        pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_w, bar_h), 2)

        st_y = bar_y + 20
        st_w = 240
        st_h = 10
        pygame.draw.rect(screen, (20, 20, 20), (bar_x, st_y, st_w, st_h))
        st_ratio = self.stamina / self.max_stamina
        pygame.draw.rect(screen, (20, 160, 40), (bar_x, st_y, int(st_w * st_ratio), st_h))
        pygame.draw.rect(screen, (150, 150, 150), (bar_x, st_y, st_w, st_h), 2)

        font = pygame.font.SysFont("timesnewroman", 24)
        txt = font.render(f"QS Bullets: {self.bullets}", True, (200, 200, 200))
        screen.blit(txt, (bar_x, st_y + 20))

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
