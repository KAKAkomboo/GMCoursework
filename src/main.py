import pygame
from src.core.settings import screen_width, screen_height, tile_size
from ui.menu.main_option import MainOption
from ui.menu.pause_option import PauseOption
from ui.menu.menu import Menu
from ui.pause_menu.pause_menu import PauseMenu
from ui.pause_menu.task_panel import TasksPanel
from ui.pause_menu.inventory_panel import InventoryPanel
from engine import Game
from src.world.сheckpoint import Checkpoint
from src.ui.menu.upgrade_menu import UpgradeMenu
from core.save_manager import SaveManager
from src.ui.elements.toast import Toast

pygame.init()
if not pygame.display.get_init():
    pygame.display.init()

def safe_set_mode(size, flags=0):
    try:
        return pygame.display.set_mode(size, flags)
    except pygame.error:
        pygame.display.init()
        return pygame.display.set_mode(size, flags)

pygame.display.set_caption("Game")
screen = safe_set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

try:
    pygame.mixer.init()
except Exception:
    pass

menu = Menu(screen)
main_option = MainOption(screen)
pause_option = PauseOption(screen)
pause_menu = PauseMenu(screen)
tasks_panel = TasksPanel(screen)
inventory_panel = InventoryPanel(screen)
toast = Toast()

mini_map = [[1] + [0] * 78 for _ in range(10)]
game = Game(screen, mini_map)
checkpoint = Checkpoint(5, 5)
upgrade_menu = UpgradeMenu()
save_manager = SaveManager()

font = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 28)

try:
    save_sound = pygame.mixer.Sound("save.wav")
    level_sound = pygame.mixer.Sound("level.wav")
except Exception:
    save_sound = None
    level_sound = None
checkpoint.set_sounds(save_sound, level_sound)

current_state = "menu"
previous_state = None
is_fullscreen = False

def recreate_ui_and_game(new_screen):
    global screen, menu, main_option, pause_option, pause_menu, tasks_panel, inventory_panel, game, checkpoint
    screen = new_screen
    menu = Menu(screen)
    main_option = MainOption(screen)
    pause_option = PauseOption(screen)
    pause_menu = PauseMenu(screen)
    tasks_panel = TasksPanel(screen)
    inventory_panel = InventoryPanel(screen)
    game = Game(screen, mini_map)
    checkpoint = Checkpoint(5, 5)
    checkpoint.set_sounds(save_sound, level_sound)

def toggle_fullscreen():
    global is_fullscreen
    try:
        if is_fullscreen:
            new_screen = safe_set_mode((screen_width, screen_height))
            is_fullscreen = False
        else:
            new_screen = safe_set_mode((0, 0), pygame.FULLSCREEN)
            is_fullscreen = True
        recreate_ui_and_game(new_screen)
    except pygame.error:
        new_screen = safe_set_mode((screen_width, screen_height))
        is_fullscreen = False
        recreate_ui_and_game(new_screen)

save_manager.load(game.player)

running = True
while running:
    if not pygame.display.get_surface():
        new_screen = safe_set_mode((screen_width, screen_height))
        recreate_ui_and_game(new_screen)

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
            current_state = "main_options"
            previous_state = "menu"
            main_option.show()
        elif action == "quit":
            running = False
        menu.draw()

    elif current_state == "main_options":
        action = main_option.handle_ev(events)
        if action == "back":
            current_state = previous_state or "menu"
            main_option.hide()
        elif action == "toggle_fullscreen":
            toggle_fullscreen()
        main_option.draw()

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
                        player_px = int(game.player.x * tile_size - game.camera_x + game.player.image.get_width() // 2)
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
                        pause_menu.show()

        game.handle_events(events)

        if not (checkpoint.menu_open or checkpoint.upgrade_open):
            game.update(keys, mouse_clicked, shoot, shoot_dir_right, lock_pressed)

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
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_p):
                current_state = previous_state or "game"
                pause_menu.hide()

        action = pause_menu.handle_ev(events)
        if action == "settings":
            current_state = "pause_options"
            previous_state = "pause"
            pause_option.show()
        elif action == "tasks":
            current_state = "tasks"
            previous_state = "pause"
            pause_menu.hide()
            tasks_panel.show()
            inventory_panel.hide()
        elif action == "inventory":
            current_state = "inventory"
            previous_state = "pause"
            pause_menu.hide()
            inventory_panel.show()
            tasks_panel.hide()
        elif action == "menu":
            current_state = "menu"
            previous_state = "pause"
            pause_menu.hide()
            tasks_panel.hide()
            inventory_panel.hide()

        pause_menu.draw()

    elif current_state == "pause_options":
        action = pause_option.handle_ev(events)
        if action == "back":
            current_state = previous_state or "pause"
            pause_option.hide()
        elif action == "toggle_fullscreen":
            toggle_fullscreen()
        pause_option.draw()

    elif current_state == "tasks":
        tasks_panel.draw()
        res = tasks_panel.handle_ev(events)
        if res == "back":
            tasks_panel.hide()
            current_state = "pause"
            previous_state = "tasks"
            pause_menu.show()

    elif current_state == "inventory":
        inventory_panel.draw()
        res = inventory_panel.handle_ev(events)
        if res == "back":
            inventory_panel.hide()
            current_state = "pause"
            previous_state = "inventory"
            pause_menu.show()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
