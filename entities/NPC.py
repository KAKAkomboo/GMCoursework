import math
import pygame
from random import randint, choice

from Settings import tile_size


class NPC(pygame.sprite.Sprite):
    def __init__(self, game, pos=(10.5, 5.5), path='',
                 scale=1.0, animation_time=180):
        super.__init__()
        self.game = game
        self.pos = pos
        self.scale = scale
        self.animation_time = animation_time

        self.idle_image = [pygame.image.load(path).convert_alpha()]
        self.walk_image = [pygame.image.load(path).convert_alpha()]
        self.attack_image = [pygame.image.load(path).convert_alpha()]
        self.death_image = [pygame.image.load(path).convert_alpha()]

        for img_list in [self.idle_image, self.walk_image, self.attack_image, self.death_image]:
            for i in range(len(img_list)):
                img_list[i] = pygame.transform.scale(img_list[i], (int(img_list[i].get_width() * scale)),
                                                     (int(img_list[i].get_height() * scale)))
                self.image = self.idle_image[0]
                self.rect = self.image.get_rect(center=(self.pos[0] * tile_size, self.pos[1] * tile_size))

                self.health = 100
                self.max_health = 100
                self.speed = 1
                self.attack_damage = 10
                self.attack_range = 1.0
                self.vision_range = 5.0
                self.alive = True
                self.state = 'idle'
                self.frame_counter = 0
                self.animation_trigger = False
                self.last_update = pygame.time.get_ticks()

                self.chasing_player = False

    def update(self):
        if self.alive:
            self.run_log()
            self.animate()
            self.rect.center = (self.pos[0] * tile_size, self.pos[0] * tile_size)
        else:
            self.animate_death()

    def run_log(self):
        player_pos = self.game.player.pos
        dist_to_player = math.dist(self.pos, player_pos)

        if dist_to_player <= self.vision_range:
            self.chasing_player = True
            if dist_to_player <= self.attack_range:
                self.state = 'attack'
                self.attack()
            else:
                self.state = 'walk'
                self.move_towards_player()
        else:
            self.chasing_player = False
            self.state = 'idle'
            if randint(0, 100) < 5:
                self.random_move()

    def move_towards_player(self):
        player_pos = self.game.player.pos
        dx = player_pos[0] - self.pos[0]
        dy = player_pos[1] - self.pos[1]
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist > 0:
            dx /= dist
            dy /= dist
            new_x = self.pos[0] + dx * self.speed
            new_y = self.pos[1] + dy * self.speed
            if self.check_wall(new_x, new_y):
                self.pos[0] = new_x
                self.pos[1] = new_y

    def attack(self):
        if self.animation_trigger:
            self.game.player.take_damage(self.attack_damage)

    def check_wall(self, x, y):
        tile_x, tile_y = int(x), int(y)
        return (tile_x, tile_y) not in self.game.map.world_map

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            self.state = 'death'

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_time:
            self.last_update = now
            self.animation_trigger = True
            if self.state == 'idle':
                self.frame_counter = (self.frame_counter + 1) % len(self.idle_images)
                self.image = self.idle_images[self.frame_counter]
            elif self.state == 'walk':
                self.frame_counter = (self.frame_counter + 1) % len(self.walk_images)
                self.image = self.walk_images[self.frame_counter]
            elif self.state == 'attack':
                self.frame_counter = (self.frame_counter + 1) % len(self.attack_images)
                self.image = self.attack_images[self.frame_counter]
        else:
            self.animation_trigger = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)
