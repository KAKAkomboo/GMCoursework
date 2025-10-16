import pygame
from Settings import *
from Ui.Menu import Menu, OptionsMenu

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
running = True

menu = Menu(screen)
options_menu = OptionsMenu(screen)
current_state = "menu"

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if current_state == "menu":
        action = menu.handle_ev(events)
        if action == "start":
            print("Запуск гри")
        elif action == "options":
            current_state = "options"
        elif action == "quit":
            running = False
        menu.draw()
    elif current_state == "options":
        action = options_menu.handle_ev(events)
        if action == "back":
            current_state = "menu"
        options_menu.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()