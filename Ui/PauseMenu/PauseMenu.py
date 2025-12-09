import pygame, os
from Ui.Buttons import Button
from Settings import screen_width, screen_height, ICONS_DIR, WHITE, GRAY

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        self.font = pygame.font.SysFont("arial", 28)

        self.options = [("settings","settings.png"),("tasks","tasks.png"),("inventory","inventory.png"),("menu","exit.png")]
        self.buttons, self.icons = [], []

        size, spacing = 48, 20
        total_w = len(self.options)*size+(len(self.options)-1)*spacing
        start_x, start_y = screen_width-total_w-40, 40

        for i,(label,icon_file) in enumerate(self.options):
            x = start_x+i*(size+spacing)
            path = os.path.join(ICONS_DIR,icon_file)
            if os.path.exists(path):
                icon = pygame.image.load(path).convert_alpha()
                icon = pygame.transform.scale(icon,(size,size))
            else:
                icon = pygame.Surface((size,size),pygame.SRCALPHA)
                pygame.draw.rect(icon,GRAY,icon.get_rect(),border_radius=6)
            self.icons.append((icon,(x,start_y)))
            self.buttons.append(Button(x,start_y,size,size,""))

        self.title = self.font.render("Pause",True,WHITE)

    def show(self): self.visible=True
    def hide(self): self.visible=False

    def draw(self):
        if not self.visible:
            return
        tx = (screen_width - self.title.get_width()) // 2
        self.screen.blit(self.title, (tx, 10))

        for btn, (icon, pos) in zip(self.buttons, self.icons):
            self.screen.blit(icon, pos)
            btn.draw(self.screen)

    def handle_ev(self, events):
        if not self.visible:
            return None
        for event in events:
            for i, btn in enumerate(self.buttons):
                if btn.handle_ev(event):
                    return self.options[i][0]
        return None
