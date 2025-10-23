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

    def update(self, keys):
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
