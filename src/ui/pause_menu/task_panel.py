import pygame
from src.core.settings import WHITE

class TasksPanel:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        
        try:
            self.font_title = pygame.font.SysFont("timesnewroman", 32, bold=True)
            self.font = pygame.font.SysFont("timesnewroman", 24)
        except:
            self.font_title = pygame.font.SysFont("arial", 32)
            self.font = pygame.font.SysFont("arial", 24)

        self.active_quests = []

    def add_quest(self, quest):
        if quest and quest not in self.active_quests:
            self.active_quests.append(quest)

    def remove_quest(self, quest_title):
        self.active_quests = [q for q in self.active_quests if q.title != quest_title]

    def show(self): 
        self.visible = True

    def hide(self): 
        self.visible = False

    def draw(self):
        if not self.visible: return
        
        current_w, current_h = self.screen.get_size()

        overlay = pygame.Surface((current_w, current_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title = self.font_title.render("Active Tasks", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(current_w // 2, 120)))

        y = 200
        if not self.active_quests:
            no_quests_text = self.font.render("No active tasks.", True, (150, 150, 150))
            self.screen.blit(no_quests_text, no_quests_text.get_rect(center=(current_w // 2, y)))
        else:
            for quest in self.active_quests:
                quest_title = self.font.render(f"- {quest.title}", True, (230, 230, 230))
                self.screen.blit(quest_title, (current_w // 2 - 300, y))
                y += 30
                quest_desc = self.font.render(f"  {quest.description}", True, (180, 180, 180))
                self.screen.blit(quest_desc, (current_w // 2 - 280, y))
                y += 40

    def handle_ev(self, events):
        if not self.visible: return None
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"
        return None
