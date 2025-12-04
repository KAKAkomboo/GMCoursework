import pygame
from Settings import tile_size


class Player:
    def __init__(self, x, y, map_instance):
        self.x = x
        self.y = y
        self.map = map_instance
        self.image = pygame.Surface((tile_size, tile_size + 32))
        self.image.fill((255, 0, 255))
        self.speed = 0.4
        self.moving = False
        self.target_x = self.x
        self.target_y = self.y
        self.health = 100
        self.max_health = 100
        self.alive = True
        self.show_death_popup = False
        self.death_x = self.x
        self.death_y = self.y

    def update(self, keys):
        if not self.alive:
            return
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
                self.speed = 1
            else:
                self.speed = 0.4

            if dx or dy:
                new_x = self.x + dx
                new_y = self.y + dy
                if (
                        self.map.is_walkable(new_x, new_y)
                        and self.map.is_walkable(new_x, new_y + 1)
                ):
                    self.target_x = new_x
                    self.target_y = new_y
                    self.moving = True

        if self.moving:
            if self.x < self.target_x:
                self.x += self.speed
            elif self.x > self.target_x:
                self.x -= self.speed
            if self.y < self.target_y:
                self.y += self.speed
            elif self.y > self.target_y:
                self.y -= self.speed

            if abs(self.x - self.target_x) < self.speed and abs(self.y - self.target_y) < self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.moving = False

    def draw(self, screen, camera_x, camera_y):
        screen.blit(self.image, (self.x * tile_size - camera_x, self.y * tile_size - camera_y))

        bar_width = 200
        bar_height = 20
        bar_x = 10
        bar_y = 10


        pygame.draw.rect(screen, (128, 128, 128), (bar_x, bar_y, bar_width, bar_height))
        health_ratio = self.health / self.max_health
        health_color = (255 * (1 - health_ratio), 255 * health_ratio, 0)
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, bar_width * health_ratio, bar_height))

        if self.show_death_popup:
            font = pygame.font.SysFont(None, 48)
            text = font.render("YOU DIED", True, (255, 0, 0))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
            screen.blit(restart_text, restart_rect)

    def take_damage(self, damage):
        if self.alive:
            self.health -= damage
            if self.health <= 0:
                self.health = 0
                self.alive = False
                self.show_death_popup = True
                self.death_x = self.x
                self.death_y = self.y
                print("Player died!")
        else:
            print(f"Player took {damage} damage!")

    def restart(self):
        self.health = self.max_health
        self.alive = True
        self.show_death_popup = False
        self.x = self.death_x
        self.y = self.death_y
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False