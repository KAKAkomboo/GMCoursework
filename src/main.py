import pygame
from src.core.settings import tile_size
from ui.menu.main_option import MainOption
from ui.menu.pause_option import PauseOption
from ui.menu.menu import Menu
from ui.pause_menu.pause_menu import PauseMenu
from ui.pause_menu.task_panel import TasksPanel
from ui.pause_menu.inventory_panel import InventoryPanel
from src.ui.menu.sub_menus import BrightnessMenu, KeySettingsMenu, PlaceholderMenu, GameOptionsMenu
from src.ui.elements.dialogue_box import DialogueBox
from engine import Game
from src.world.сheckpoint import Checkpoint
from src.ui.menu.upgrade_menu import UpgradeMenu
from core.save_manager import SaveManager
from src.ui.elements.toast import Toast
from src.ui.elements.death_screen import DeathScreen

pygame.init()
if not pygame.display.get_init():
    pygame.display.init()

info = pygame.display.Info()
initial_screen_width = info.current_w
initial_screen_height = info.current_h

def safe_set_mode(size, flags=0):
    try:
        return pygame.display.set_mode(size, flags)
    except pygame.error:
        pygame.display.init()
        return pygame.display.set_mode(size, flags)

pygame.display.set_caption("Game")
screen = safe_set_mode((initial_screen_width, initial_screen_height), pygame.RESIZABLE)
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
death_screen = DeathScreen(screen.get_width(), screen.get_height())
dialogue_box = DialogueBox(screen)

brightness_menu = BrightnessMenu(screen)
key_settings_menu = KeySettingsMenu(screen)
game_options_menu = GameOptionsMenu(screen)
network_menu = PlaceholderMenu(screen, "Network Settings")
pc_menu = PlaceholderMenu(screen, "PC Settings")

mini_map = [[1] + [0] * 78 for _ in range(10)]
game = Game(screen, mini_map)
game.set_dialogue_system(dialogue_box) # Connect dialogue system

checkpoints = [
    Checkpoint(5, 5),
    Checkpoint(70, 5)
]

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

for cp in checkpoints:
    cp.set_sounds(save_sound, level_sound)

current_state = "menu"
previous_state = None
is_maximized = True

def update_screen_references(new_screen):
    global screen
    screen = new_screen

    menu.screen = screen
    menu.recalculate_layout()
    
    main_option.screen = screen
    main_option.recalculate_layout()
    
    pause_option.screen = screen
    pause_option.recalculate_layout()
    
    pause_menu.screen = screen
    pause_menu.recalculate_layout()
    
    tasks_panel.screen = screen
    inventory_panel.screen = screen
    
    death_screen.w = screen.get_width()
    death_screen.h = screen.get_height()
    
    dialogue_box.screen = screen

    brightness_menu.screen = screen
    brightness_menu.recalculate_layout()
    key_settings_menu.screen = screen
    key_settings_menu.recalculate_layout()
    game_options_menu.screen = screen
    game_options_menu.recalculate_layout()
    network_menu.screen = screen
    network_menu.recalculate_layout()
    pc_menu.screen = screen
    pc_menu.recalculate_layout()
    
    game.screen = screen

def toggle_fullscreen():
    global is_maximized
    try:
        if is_maximized:
            new_screen = safe_set_mode((1280, 720), pygame.RESIZABLE)
            is_maximized = False
        else:
            info = pygame.display.Info()
            new_screen = safe_set_mode((info.current_w, info.current_h), pygame.RESIZABLE)
            is_maximized = True
        update_screen_references(new_screen)
    except pygame.error:
        new_screen = safe_set_mode((1280, 720), pygame.RESIZABLE)
        is_maximized = False
        update_screen_references(new_screen)

if save_manager.load(game.player):
    for cp in checkpoints:
        if cp.x == game.player.respawn_x and cp.y == game.player.respawn_y:
            cp.bonfire_lit = True

running = True
while running:
    if not pygame.display.get_surface():
        new_screen = safe_set_mode((initial_screen_width, initial_screen_height), pygame.RESIZABLE)
        update_screen_references(new_screen)

    events = pygame.event.get()
    keys = pygame.key.get_pressed()
    now = pygame.time.get_ticks()

    real_dt = clock.get_time()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.VIDEORESIZE:
            update_screen_references(safe_set_mode(event.size, pygame.RESIZABLE))

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
            current_state = "menu"
            main_option.hide()
        elif action == "game_options":
            current_state = "game_options"
            previous_state = "main_options"
        elif action == "brightness":
            current_state = "brightness"
            previous_state = "main_options"
        elif action == "key_settings":
            current_state = "key_settings"
            previous_state = "main_options"
        elif action == "network_settings":
            current_state = "network_settings"
            previous_state = "main_options"
        elif action == "pc_settings":
            current_state = "pc_settings"
            previous_state = "main_options"
        main_option.draw()

    elif current_state == "game_options":
        for event in events:
            res = game_options_menu.handle_ev(event)
            if res == "back":
                current_state = "main_options"
        game_options_menu.draw()
        
    elif current_state == "brightness":
        for event in events:
            res = brightness_menu.handle_ev(event)
            if res == "back":
                current_state = "main_options"
        brightness_menu.draw()
        
    elif current_state == "key_settings":
        for event in events:
            res = key_settings_menu.handle_ev(event)
            if res == "back":
                current_state = "main_options"
        key_settings_menu.draw()

    elif current_state == "network_settings":
        for event in events:
            res = network_menu.handle_ev(event)
            if res == "back":
                current_state = "main_options"
        network_menu.draw()

    elif current_state == "pc_settings":
        for event in events:
            res = pc_menu.handle_ev(event)
            if res == "back":
                current_state = "main_options"
        pc_menu.draw()

    elif current_state == "game":
        mouse_clicked = False
        shoot = False
        shoot_dir_right = True
        lock_pressed = False
        activate_checkpoint = False
        
        any_menu_open = any(cp.menu_open or cp.upgrade_open for cp in checkpoints)
        dialogue_active = dialogue_box.active


        if dialogue_active:
            dialogue_box.handle_input(events)
        else:
            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_clicked = True
                    elif event.button == 3:
                        if any_menu_open:
                            for cp in checkpoints:
                                cp.close_all()
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
                        handled_by_cp = False
                        for cp in checkpoints:
                            if cp.upgrade_open:
                                cp.upgrade_open = False
                                cp.menu_open = True
                                handled_by_cp = True
                            elif cp.menu_open:
                                cp.close_all()
                                handled_by_cp = True
                        
                        if not handled_by_cp:
                            current_state = "pause"
                            previous_state = "game"
                            pause_menu.show()

        game.handle_events(events)

        if not any_menu_open and not dialogue_active:
            game.update(keys, mouse_clicked, shoot, shoot_dir_right, lock_pressed)

        if not dialogue_active:
            for fnpc in game.friendly_npcs:
                fnpc.handle_input(events)

        for cp in checkpoints:
            cp.update(game.player, now)
            if activate_checkpoint and cp.active:
                cp.open_menu(game.player)

        game.draw()

        if brightness_menu.brightness < 1.0:
            darkness = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            alpha = int((1.0 - brightness_menu.brightness) * 255)
            darkness.fill((0, 0, 0, alpha))
            screen.blit(darkness, (0, 0))

        for cp in checkpoints:
            btns = cp.draw(screen, game.camera_x, game.camera_y, font, font_small)
            if cp.menu_open and not cp.upgrade_open:
                cp.handle_menu_keys(game.player, toast, game, keys, now)
                cp.handle_menu_mouse(game.player, toast, game, btns, now)
            if cp.upgrade_open:
                cb, bb = upgrade_menu.draw(screen, game.player, font, font_small)
                res = upgrade_menu.handle_input(game.player, events, keys, cb, bb, toast, level_sound)
                if res == "close":
                    cp.close_all()
                elif res == "back":
                    cp.upgrade_open = False
                    cp.menu_open = True

        dialogue_box.update(real_dt)
        dialogue_box.draw()

        toast.draw(screen, font_small)

        if not game.player.alive:
            death_screen.show()
            death_screen.update()
            death_screen.draw(screen)
            if keys[pygame.K_r]:
                game.player.restart()
                game.respawn_enemies()
                death_screen.hide()
        else:
            death_screen.hide()

        if not any_menu_open and not dialogue_active and keys[pygame.K_F5]:
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

        game.draw()
        pause_menu.draw()

    elif current_state == "pause_options":
        action = pause_option.handle_ev(events)
        if action == "back":
            current_state = previous_state or "pause"
            pause_option.hide()
        elif action == "toggle_fullscreen":
            toggle_fullscreen()
        
        game.draw()
        pause_option.draw()

    elif current_state == "tasks":
        game.draw()
        tasks_panel.draw()
        res = tasks_panel.handle_ev(events)
        if res == "back":
            tasks_panel.hide()
            current_state = "pause"
            previous_state = "tasks"
            pause_menu.show()

    elif current_state == "inventory":
        game.draw()
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
