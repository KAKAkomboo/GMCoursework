import pygame
import math
from src.core.settings import tile_size

class FriendlyNPC(pygame.sprite.Sprite):
    def __init__(self, game, name="Villager", pos=(8.5, 6.5), scale=1.0, animation_time=220):
        super().__init__()
        self.game = game
        self.name = str(name)
        self.pos = (float(pos[0]), float(pos[1]))
        self.scale = float(scale)
        self.animation_time = int(animation_time)

        size = (int(tile_size * self.scale), int(tile_size * self.scale))
        self.idle_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        pygame.draw.rect(self.idle_image[0], (180, 180, 0), self.idle_image[0].get_rect()) # Yellow-ish

        self.image = self.idle_image[0]
        self.rect = self.image.get_rect(center=(int(self.pos[0] * tile_size), int(self.pos[1] * tile_size)))

        self.interact_range = 2.0
        self.is_player_near = False
        
        # Dialogue Tree
        self.dialogue_tree = self.create_dialogue_tree()

    def create_dialogue_tree(self):
        # Unique dialogue based on name
        if self.name == "Elder":
            return {
                "start": {
                    "text": "Знову ти? Твої кроки звучать занадто гучно для цього мертвого місця...",
                    "next": "elder_node_2"
                },
                "elder_node_2": {
                    "text": "Шукаєш іскру? Чи просто хочеш зігріти свої кістки біля мого вогню?",
                    "choices": [
                        {"text": "Шукаю іскру.", "next": "elder_quest_start"},
                        {"text": "Просто відпочиваю.", "next": "exit"}
                    ]
                },
                "elder_quest_start": {
                    "text": "Іскра... Вона ховається у темряві. Принеси мені її, і я віддячу.",
                    "next": "exit"
                }
            }
        else:
            return {
                "start": {
                    "text": "Ти... хто ти? Не підходь. Я бачив, що робить кров.",
                    "next": "villager_node_2"
                },
                "villager_node_2": {
                    "text": "Всі вони... перетворилися. Скоро і я. Залиш мене.",
                    "choices": [
                        {"text": "Я можу допомогти.", "next": "villager_help"},
                        {"text": "Я піду.", "next": "exit"}
                    ]
                },
                "villager_help": {
                    "text": "Допомогти? Ніхто не може. Тільки смерть... вона звільнить.",
                    "next": "exit"
                }
            }

    def update(self):
        self.check_proximity()
        self.rect.center = (int(self.pos[0] * tile_size), int(self.pos[1] * tile_size))

    def check_proximity(self):
        player_pos = (self.game.player.x, self.game.player.y)
        dist = math.dist(self.pos, player_pos)
        self.is_player_near = dist <= self.interact_range

    def handle_input(self, events):
        if not self.is_player_near: return

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_e:
                if hasattr(self.game, "start_dialogue"):
                    self.game.start_dialogue(self.name, self.dialogue_tree)

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.pos[0] * tile_size - camera_x - (self.rect.width / 2)
        screen_y = self.pos[1] * tile_size - camera_y - (self.rect.height / 2)
        screen.blit(self.image, (screen_x, screen_y))

        if self.is_player_near:
            self.draw_hint(screen, screen_x, screen_y)

    def draw_hint(self, screen, x, y):
        font = pygame.font.SysFont(None, 24)
        text = font.render("E", True, (255, 255, 255))
        pygame.draw.circle(screen, (0, 0, 0), (int(x + self.rect.width/2), int(y - 20)), 15)
        pygame.draw.circle(screen, (255, 255, 255), (int(x + self.rect.width/2), int(y - 20)), 15, 2)
        screen.blit(text, (x + self.rect.width/2 - text.get_width()/2, y - 28))
