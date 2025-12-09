import pygame
from Settings import screen_width, screen_height, tile_size
from Ui.Menu import Menu, OptionsMenu
from Ui.PauseMenu import PauseMenu
from game import Game
from smthForMap.Checkpoint import Checkpoint
from smthForMap.UpgradeMenu import UpgradeMenu
from smthForMap.SaveManager import SaveManager
from Ui.Toast import Toast

pygame.init()
pygame.display.set_caption("Game")

screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
running = True

try:
    pygame.mixer.init()
except Exception:
    pass

menu = Menu(screen)
options_menu = OptionsMenu(screen)
pause_menu = PauseMenu(screen)

mini_map = [[1] + [0] * 78 for _ in range(10)]
game = Game(screen, mini_map)

current_state = "menu"
previous_state = None
is_fullscreen = False

checkpoint = Checkpoint(5, 5)
upgrade_menu = UpgradeMenu()
save_manager = SaveManager()
toast = Toast()

font = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 28)

try:
    save_sound = pygame.mixer.Sound("save.wav")
    level_sound = pygame.mixer.Sound("level.wav")
except Exception:
    save_sound = None
    level_sound = None
checkpoint.set_sounds(save_sound, level_sound)

def recreate_ui_and_game(new_screen):
    global screen, menu, options_menu, pause_menu, game, checkpoint
    screen = new_screen
    menu = Menu(screen)
    options_menu = OptionsMenu(screen)
    pause_menu = PauseMenu(screen)
    game = Game(screen, mini_map)
    checkpoint = Checkpoint(5, 5)
    checkpoint.set_sounds(save_sound, level_sound)

save_manager.load(game.player)

while running:
    events = pygame.event.get()
    keys = pygame.key.get_pressed()

    # Global quit
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
            try:
                if is_fullscreen:
                    new_screen = pygame.display.set_mode((screen_width, screen_height))
                    is_fullscreen = False
                else:
                    new_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    is_fullscreen = True
                recreate_ui_and_game(new_screen)
            except Exception:
                new_screen = pygame.display.set_mode((screen_width, screen_height))
                is_fullscreen = False
                recreate_ui_and_game(new_screen)
        options_menu.draw()

    elif current_state == "game":
        mouse_clicked = False
        shoot = False
        shoot_dir_right = True
        lock_pressed = False
        activate_checkpoint = False

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
                elif event.button == 3:
                    if checkpoint.menu_open or checkpoint.upgrade_open:
                        checkpoint.close_all()
                    else:
                        shoot = True
                        mx, _ = pygame.mouse.get_pos()
                        player_px = int(
                            game.player.x * tile_size
                            - game.camera_x
                            + game.player.image.get_width() // 2
                        )
                        shoot_dir_right = mx >= player_px

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    lock_pressed = True
                elif event.key == pygame.K_e:
                    activate_checkpoint = True
                elif event.key == pygame.K_ESCAPE:
                    if checkpoint.upgrade_open:
                        checkpoint.upgrade_open = False
                        checkpoint.menu_open = True
                    elif checkpoint.menu_open:
                        checkpoint.close_all()
                    else:
                        current_state = "pause"
                        previous_state = "game"

        game.handle_events(events)

        if not (checkpoint.menu_open or checkpoint.upgrade_open):
            game.update(
                keys,
                mouse_clicked=mouse_clicked,
                shoot=shoot,
                shoot_dir_right=shoot_dir_right,
                lock_pressed=lock_pressed
            )

        for fnpc in game.friendly_npcs:
            fnpc.handle_input(events)

        checkpoint.update_active(game.player)
        if activate_checkpoint and checkpoint.active:
            checkpoint.open_menu(game.player)

        btns = checkpoint.draw(screen, game.camera_x, game.camera_y, font, font_small)
        if checkpoint.menu_open and not checkpoint.upgrade_open:
            checkpoint.handle_menu_keys(game.player, keys, pygame.time.get_ticks(), toast)
            checkpoint.handle_menu_mouse(game.player, toast, btns, pygame.time.get_ticks())

        if checkpoint.upgrade_open:
            cb, bb = upgrade_menu.draw(screen, game.player, font, font_small)
            res = upgrade_menu.handle_input(game.player, events, keys, cb, bb, toast, level_sound)
            if res == "close":
                checkpoint.close_all()
            elif res == "back":
                checkpoint.upgrade_open = False
                checkpoint.menu_open = True

        game.draw()
        toast.draw(screen, font_small)
        checkpoint.draw_bonfire(screen, game.camera_x, game.camera_y)

        if not game.player.alive and keys[pygame.K_r]:
            game.player.restart()
            game.reset_npcs()

        if not checkpoint.menu_open and not checkpoint.upgrade_open and keys[pygame.K_F5]:
            save_manager.save(game.player)
            toast.show("Updated checkpoint.", 1200)

    elif current_state == "pause":
        # Rule 2: ESC in pause resumes game; menu only via button
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    current_state = previous_state or "game"

        action = pause_menu.handle_ev(events)
        if action == "settings":
            current_state = "options"
            previous_state = "pause"
        elif action == "tasks":
            current_state = "tasks"
            previous_state = "pause"
        elif action == "inventory":
            current_state = "inventory"
            previous_state = "pause"
        elif action == "menu":
            # Only path to main menu is via this button
            current_state = "menu"
            previous_state = "pause"

        pause_menu.draw()

    elif current_state == "tasks":
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = font.render("Tasks", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 120)))

        stub_lines = [
            "- Reach the first bonfire",
            "- Defeat the Hollow Knight",
            "- Collect 5 soul fragments",
        ]
        y = 200
        for line in stub_lines:
            txt = font_small.render(line, True, (230, 230, 230))
            screen.blit(txt, (screen.get_width() // 2 - 220, y))
            y += 30

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_state = "pause"
                previous_state = "tasks"

    # ---------------- INVENTORY STATE ----------------
    elif current_state == "inventory":
        overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = font.render("Inventory", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 120)))

        cell_w, cell_h = 80, 80
        cols, rows = 6, 3
        start_x = screen.get_width() // 2 - (cols * cell_w + (cols - 1) * 10) // 2
        start_y = 200
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(
                    start_x + c * (cell_w + 10),
                    start_y + r * (cell_h + 10),
                    cell_w,
                    cell_h
                )
                pygame.draw.rect(screen, (200, 200, 200), rect, 2)

        hint = font_small.render("Press ESC to go back", True, (220, 220, 220))
        screen.blit(hint, hint.get_rect(center=(screen.get_width() // 2, screen.get_height() - 80)))

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                current_state = "pause"
                previous_state = "inventory"


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
