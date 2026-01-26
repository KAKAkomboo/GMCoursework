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
        self.talk_image = [pygame.Surface(size, pygame.SRCALPHA).convert_alpha()]
        pygame.draw.rect(self.idle_image[0], (180, 180, 0), self.idle_image[0].get_rect())
        pygame.draw.rect(self.talk_image[0], (255, 220, 120), self.talk_image[0].get_rect())

        self.image = self.idle_image[0]
        self.rect = self.image.get_rect(center=(int(self.pos[0] * tile_size), int(self.pos[1] * tile_size)))


        self.state = "idle"
        self.last_update = pygame.time.get_ticks()
        self.animation_trigger = False
        self.frame_counter = 0

        self.interact_range = 1.5
        self.is_player_near = False
        self.is_dialog_open = False
        self.dialog_index = 0
        self.menu_index = 0

        self.dialog_lines = [
            f"{self.name}: Hey there, traveler.",
            "The roads ahead are dangerous. Stay sharp.",
            "If you need guidance, I can share a few tips."
        ]

        self.menu_options = [
            "Ask about the area",
            "Trade (simple)",
            "Request a small quest",
            "Leave"
        ]

        self.quest_given = False
        self.quest_completed = False
        self.trade_done = False

    def update(self, dt=None):
        self.check_proximity()
        self.animate()

        self.rect.center = (int(self.pos[0] * tile_size), int(self.pos[1] * tile_size))

    def check_proximity(self):
        player_pos = (self.game.player.x, self.game.player.y)
        dist = math.dist(self.pos, player_pos)
        self.is_player_near = dist <= self.interact_range

    def handle_input(self, events):
        if not self.is_player_near:
            return

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_e and not self.is_dialog_open:
                    self.open_dialog()
                elif self.is_dialog_open:
                    if e.key == pygame.K_RETURN:
                        if not getattr(self, "in_menu_mode", False):
                            self.advance_dialog_or_select()
                        else:
                            self.apply_menu_selection()
                    elif e.key == pygame.K_UP and getattr(self, "in_menu_mode", False):
                        self.menu_index = max(0, self.menu_index - 1)
                    elif e.key == pygame.K_DOWN and getattr(self, "in_menu_mode", False):
                        self.menu_index = min(len(self.menu_options) - 1, self.menu_index + 1)
                    elif e.key == pygame.K_ESCAPE:
                        self.close_dialog()

        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_e and not self.is_dialog_open:
                    self.open_dialog()
                elif self.is_dialog_open:
                    if e.key == pygame.K_RETURN:
                        self.advance_dialog_or_select()
                    elif e.key == pygame.K_UP:
                        self.menu_index = max(0, self.menu_index - 1)
                    elif e.key == pygame.K_DOWN:
                        self.menu_index = min(len(self.menu_options) - 1, self.menu_index + 1)
                    elif e.key == pygame.K_ESCAPE:
                        self.close_dialog()

    def open_dialog(self):
        self.is_dialog_open = True
        self.state = "talk"
        self.image = self.talk_image[0]
        self.dialog_index = 0
        self.menu_index = 0

    def close_dialog(self):
        self.is_dialog_open = False
        self.in_menu_mode = False  # <-- reset
        self.state = "idle"
        self.image = self.idle_image[0]

    def advance_dialog_or_select(self):
        if self.dialog_index < len(self.dialog_lines) - 1:
            self.dialog_index += 1
        else:
            self.dialog_index = len(self.dialog_lines) - 1
            self.in_menu_mode = True  # <-- NEW FLAG

    def apply_menu_selection(self):
        choice = self.menu_options[self.menu_index]

        if choice == "Ask about the area":
            if hasattr(self.game, "hud") and hasattr(self.game.hud, "show_message"):
                self.game.hud.show_message("Villager: Bandits lurk near the old bridge. Keep your shield up.")
        elif choice == "Trade (simple)":
            if hasattr(self.game.player, "currency") and self.game.player.currency >= 5 and not self.trade_done:
                self.game.player.currency -= 5
                if hasattr(self.game.player, "heal"):
                    self.game.player.heal(10)
                self.trade_done = True
                if hasattr(self.game, "hud") and hasattr(self.game.hud, "show_message"):
                    self.game.hud.show_message("Villager: Here, a tonic. Safe travels.")
            else:
                if hasattr(self.game, "hud") and hasattr(self.game.hud, "show_message"):
                    self.game.hud.show_message("Villager: You need 5 coins for a tonic.")
        elif choice == "Request a small quest":
            if not self.quest_given:
                self.quest_given = True
                if hasattr(self.game, "hud") and hasattr(self.game.hud, "show_message"):
                    self.game.hud.show_message("Quest: Bring me 1 herb from the forest.")
            else:
                if hasattr(self.game.player, "has_item") and self.game.player.has_item("Herb"):
                    self.quest_completed = True
                    if hasattr(self.game.player, "add_currency"):
                        self.game.player.add_currency(10)
                    if hasattr(self.game.player, "remove_item"):
                        self.game.player.remove_item("Herb")
                    if hasattr(self.game, "hud") and hasattr(self.game.hud, "show_message"):
                        self.game.hud.show_message("Villager: Thank you! Here are 10 coins.")
                else:
                    if hasattr(self.game, "hud") and hasattr(self.game.hud, "show_message"):
                        self.game.hud.show_message("Villager: Do you have the herb?")
        elif choice == "Leave":
            self.close_dialog()

    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_time:
            self.last_update = now
            self.animation_trigger = True
            self.frame_counter = (self.frame_counter + 1) % 1
        else:
            self.animation_trigger = False

    def draw(self, screen, camera_x, camera_y):
        screen_x = self.pos[0] * tile_size - camera_x - (self.rect.width / 2)
        screen_y = self.pos[1] * tile_size - camera_y - (self.rect.height / 2)
        screen.blit(self.image, (screen_x, screen_y))

        if self.is_player_near and not self.is_dialog_open:
            self.draw_hint(screen, screen_x, screen_y, "Press [E] to talk")

        if self.is_dialog_open:
            self.draw_dialog_ui(screen)

    def draw_hint(self, screen, npc_screen_x, npc_screen_y, text):
        font = pygame.font.SysFont(None, 18)
        txt = font.render(text, True, (255, 255, 255))
        padding = 6
        bubble_w = txt.get_width() + padding * 2
        bubble_h = txt.get_height() + padding * 2
        bubble_x = npc_screen_x + (self.rect.width // 2) - (bubble_w // 2)
        bubble_y = npc_screen_y - 30

        pygame.draw.rect(screen, (0, 0, 0), (bubble_x, bubble_y, bubble_w, bubble_h), border_radius=6)
        pygame.draw.rect(screen, (255, 255, 255), (bubble_x, bubble_y, bubble_w, bubble_h), 1, border_radius=6)
        screen.blit(txt, (bubble_x + padding, bubble_y + padding))

    def draw_dialog_ui(self, screen):
        width, height = screen.get_size()
        box_h = int(height * 0.35)
        box_y = height - box_h - 40

        pygame.draw.rect(screen, (20, 20, 20), (0, box_y, width, box_h))
        pygame.draw.rect(screen, (180, 180, 180), (0, box_y, width, box_h), 2)

        font_title = pygame.font.SysFont(None, 24)
        font_body = pygame.font.SysFont(None, 22)

        title_text = font_title.render(self.name, True, (255, 255, 255))
        screen.blit(title_text, (16, box_y + 12))

        line = self.dialog_lines[self.dialog_index]
        body_text = font_body.render(line, True, (230, 230, 230))
        screen.blit(body_text, (16, box_y + 42))

        start_y = box_y + 80
        for i, opt in enumerate(self.menu_options):
            color = (255, 255, 255) if i == self.menu_index else (180, 180, 180)
            opt_text = font_body.render(f"- {opt}", True, color)
            screen.blit(opt_text, (30, start_y + i * 26))

        footer = font_body.render("Enter: select / continue   Up/Down: navigate   Esc: leave", True, (160, 160, 160))
        screen.blit(footer, (16, box_y + box_h - 30))
