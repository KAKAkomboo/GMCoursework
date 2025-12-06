# Main.py
import pygame
from Settings import screen_width, screen_height, tile_size
from Ui.Menu import Menu, OptionsMenu
from game import Game

pygame.init()
pygame.display.set_caption("Game")
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
running = True

menu = Menu(screen)
options_menu = OptionsMenu(screen)

# Example mini_map (10 rows x 80 cols)
mini_map = [[1] + [0] * 78 for _ in range(10)]

game = Game(screen, mini_map)
current_state = "menu"
previous_state = None
is_fullscreen = False

def recreate_ui_and_game(new_screen):
    """
    Recreate UI and game objects when the display mode changes.
    Keeps the same mini_map and attempts to preserve game state by creating a new Game.
    """
    global screen, menu, options_menu, game
    screen = new_screen
    menu = Menu(screen)
    options_menu = OptionsMenu(screen)
    game = Game(screen, mini_map)

while running:
    events = pygame.event.get()
    keys = pygame.key.get_pressed()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if current_state == "menu":
        action = menu.handle_ev(events)
        if action == "start":
            current_state = "game"
            previous_state = "menu"
        elif action == "options":
            current_state = "options"
            previous_state = "menu"
        elif action == "quit":
            running = False
        menu.draw()

    elif current_state == "options":
        action = options_menu.handle_ev(events)
        if action == "back":
            current_state = previous_state or "menu"
        elif action == "toggle_fullscreen":
            if is_fullscreen:
                new_screen = pygame.display.set_mode((screen_width, screen_height))
                is_fullscreen = False
            else:
                new_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                is_fullscreen = True
            recreate_ui_and_game(new_screen)
        options_menu.draw()

    elif current_state == "game":
        mouse_clicked = False
        shoot = False
        shoot_dir_right = True
        lock_pressed = False

        # Collect input flags
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
                elif event.button == 3:
                    shoot = True
                    mx, my = pygame.mouse.get_pos()
                    player_px = int(game.player.x * tile_size - game.camera_x + game.player.image.get_width() // 2)
                    shoot_dir_right = mx >= player_px
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    lock_pressed = True

        # Let game handle higher-level events (pause/menu)
        action = game.handle_events(events)
        if action == "menu":
            current_state = "menu"
            previous_state = "game"
        elif action == "pause":
            current_state = "pause"
            previous_state = "game"

        # Update game and pass input flags (game.update forwards lock_pressed to player)
        game.update(keys, mouse_clicked=mouse_clicked, shoot=shoot, shoot_dir_right=shoot_dir_right, lock_pressed=lock_pressed)
        game.draw()

        # Restart handling when player is dead
        if not game.player.alive and keys[pygame.K_r]:
            game.player.restart()
            game.reset_npcs()

    elif current_state == "pause":
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    current_state = previous_state or "game"
                elif event.key == pygame.K_ESCAPE:
                    current_state = "menu"
                    previous_state = "pause"
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont(None, 48)
        text = font.render("PAUSED - Press P to resume", True, (255, 255, 255))
        rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(text, rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
