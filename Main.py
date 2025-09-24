import pygame
from ui import Menu
from Settings import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("SMTH")
    clock = pygame.time.Clock()

    menu = Menu

    running = True
    in_menu = True

    while running:
        if in_menu:
            choice = menu.run()
            if choice == "start":
                in_menu = False
            elif choice == "options":
                print(">>> Тут може бути меню налаштувань")
            elif choice == "quit":
                running = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((0, 0, 0))
            pygame.display.flip()
            clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()