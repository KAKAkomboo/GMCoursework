import pygame
from Settings import *
from Ui.Menu import *

def main():
    pygame.init()
    menu = Menu(SCREEN)

    clock = pygame.time.Clock()
    running = True

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        action = menu.handle_ev(events)
        if action == "start":
            print("Starting the game")
        elif action == "options":
            print("Opening options")
        elif action == "quit":
            running = False

        menu.draw()

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()