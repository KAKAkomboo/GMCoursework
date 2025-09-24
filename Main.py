import pygame

from Settings import *
from Ui import Menu

def main():

    menu = Menu(SCREEN)

    clock = pygame.time.Clock()
    running = True

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        action = menu.event_h(events)
        if action == "start":
            print("Starting the game")
        elif action == "options":
            print("Opening options")
        elif action == "quit":
            running = False

        menu.update()
        menu.draw()

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

if __name__ == "__main__":
    main()