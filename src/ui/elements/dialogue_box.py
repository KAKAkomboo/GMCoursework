import pygame
from src.core.settings import screen_width, screen_height

class DialogueBox:
    def __init__(self, screen):
        self.screen = screen
        self.active = False
        self.current_node = None
        self.dialogue_tree = {}
        self.npc_name = ""

        self.height = 200
        self.padding = 20
        self.margin_bottom = 30 

        try:
            self.font_text = pygame.font.SysFont("timesnewroman", 28)
            self.font_choice = pygame.font.SysFont("timesnewroman", 26, bold=True)
            self.font_name = pygame.font.SysFont("timesnewroman", 30, bold=True)
        except:
            self.font_text = pygame.font.SysFont(None, 28)
            self.font_choice = pygame.font.SysFont(None, 26)
            self.font_name = pygame.font.SysFont(None, 30)

        self.text_to_render = ""
        self.current_char = 0
        self.text_speed = 1 
        self.text_timer = 0
        self.is_text_complete = False

        self.choice_index = 0
        self.choice_rects = []

        self.continue_icon = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(self.continue_icon, (200, 200, 200), [(0, 0), (10, 5), (0, 10)])
        self.icon_alpha = 255
        self.icon_alpha_dir = -5

    def start(self, name, tree):
        self.npc_name = name
        self.dialogue_tree = tree
        self.set_node("start")
        self.active = True

    def set_node(self, node_id):
        if node_id in self.dialogue_tree:
            self.current_node = self.dialogue_tree[node_id]
            self.text_to_render = self.current_node.get("text", "...")
            self.current_char = 0
            self.is_text_complete = False
            self.choice_index = 0
        else:
            self.close()

    def close(self):
        self.active = False
        self.current_node = None

    def handle_input(self, events):
        if not self.active: return False

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close()
                    return True
                
                if not self.is_text_complete:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.current_char = len(self.text_to_render)
                        self.is_text_complete = True
                        return True
                else:
                    if "choices" in self.current_node:
                        if event.key == pygame.K_w or event.key == pygame.K_UP:
                            self.choice_index = (self.choice_index - 1) % len(self.current_node["choices"])
                        elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                            self.choice_index = (self.choice_index + 1) % len(self.current_node["choices"])
                        elif event.key == pygame.K_RETURN:
                            self.select_choice(self.choice_index)
                    else:
                        if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                            next_id = self.current_node.get("next")
                            if next_id:
                                self.set_node(next_id)
                            else:
                                self.close()
                return True

        return True 

    def select_choice(self, index):
        choice = self.current_node["choices"][index]
        next_id = choice.get("next")
        
        if next_id == "exit":
            self.close()
        else:
            self.set_node(next_id)

    def update(self, dt):
        if not self.active: return
        
        if not self.is_text_complete:
            self.text_timer += dt
            if self.text_timer > 20: 
                self.text_timer = 0
                self.current_char += self.text_speed
                if self.current_char >= len(self.text_to_render):
                    self.is_text_complete = True
                    self.current_char = len(self.text_to_render)
        
        self.icon_alpha += self.icon_alpha_dir
        if self.icon_alpha <= 100 or self.icon_alpha >= 255:
            self.icon_alpha_dir *= -1

    def draw(self):
        if not self.active or not self.current_node: return

        current_w, current_h = self.screen.get_size()

        width = int(current_w * 0.9)
        x = (current_w - width) // 2
        y = current_h - self.height - self.margin_bottom

        s = pygame.Surface((width, self.height), pygame.SRCALPHA)
        s.fill((15, 15, 20, 230)) 
        self.screen.blit(s, (x, y))

        pygame.draw.rect(self.screen, (180, 150, 90), (x, y, width, self.height), 2)

        name_surf = self.font_name.render(self.npc_name, True, (200, 180, 100))
        self.screen.blit(name_surf, (x + self.padding, y + 15))

        text_start_y = y + 50
        visible_text = self.text_to_render[:int(self.current_char)]

        text_end_y = self.draw_text_wrapped(
            visible_text, 
            x + self.padding, 
            text_start_y, 
            width - self.padding*2
        )

        if self.is_text_complete and "choices" not in self.current_node:
            icon_surf = self.continue_icon.copy()
            icon_surf.set_alpha(self.icon_alpha)
            self.screen.blit(icon_surf, (x + width - 30, y + self.height - 25))

        if self.is_text_complete and "choices" in self.current_node:
            choice_y = text_end_y + 20
            
            for i, choice in enumerate(self.current_node["choices"]):
                color = (150, 150, 150)
                indicator_visible = False
                
                if i == self.choice_index:
                    color = (255, 255, 255)
                    indicator_visible = True
                
                txt_surf = self.font_choice.render(choice['text'], True, color)
                rect = txt_surf.get_rect(center=(x + width // 2, choice_y))

                if choice_y + txt_surf.get_height() < y + self.height:
                    self.screen.blit(txt_surf, rect)
                    
                    if indicator_visible:
                        pygame.draw.circle(self.screen, (200, 180, 120), (rect.left - 20, rect.centery), 5)

                choice_y += txt_surf.get_height() + 10

    def draw_text_wrapped(self, text, x, y, max_width):
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            w, h = self.font_text.size(test_line)
            if w < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))

        line_height = self.font_text.get_height() + 5
        current_y = y
        
        for line in lines:
            surf = self.font_text.render(line, True, (220, 220, 220))
            self.screen.blit(surf, (x, current_y))
            current_y += line_height
            
        return current_y
