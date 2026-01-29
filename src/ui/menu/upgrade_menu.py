import pygame

class UpgradeMenu:
    def __init__(self):
        self.attributes = ["Health", "Stamina", "Dexterity", "Strength", "Blood Shade", "Sacrament"]
        self.selected_index = 0
        self.base_cost = 100
        self.cost_scale = 1.1
        self.confirm_disabled = False

    def current_values(self, player):
        vals = {
            "Health": getattr(player, "max_health", 100),
            "Stamina": getattr(player, "max_stamina", 100),
            "Dexterity": getattr(player, "dexterity", 0),
            "Strength": getattr(player, "strength", 0),
            "Blood Shade": getattr(player, "blood_shade", 0),
            "Sacrament": getattr(player, "sacrament", 0),
        }
        return vals

    def next_values(self, player):
        vals = self.current_values(player).copy()
        vals["Health"] = vals["Health"] + 10
        vals["Stamina"] = vals["Stamina"] + 10
        vals["Dexterity"] = vals["Dexterity"] + 1
        vals["Strength"] = vals["Strength"] + 1
        vals["Blood Shade"] = vals["Blood Shade"] + 1
        vals["Sacrament"] = vals["Sacrament"] + 1
        return vals

    def get_level_for_attr(self, player, attr):

        if attr == "Health":
            return (getattr(player, "max_health", 100) - 100) // 10
        elif attr == "Stamina":
            return (getattr(player, "max_stamina", 100) - 100) // 10
        elif attr == "Dexterity":
            return getattr(player, "dexterity", 0)
        elif attr == "Strength":
            return getattr(player, "strength", 0)
        elif attr == "Blood Shade":
            return getattr(player, "blood_shade", 0)
        elif attr == "Sacrament":
            return getattr(player, "sacrament", 0)
        return 0

    def cost_for(self, player, attr):
        current_level = self.get_level_for_attr(player, attr)
        cost = int(self.base_cost * (self.cost_scale ** current_level))
        return max(cost, 1)

    def apply_upgrade(self, player, attr):
        if attr == "Health":
            player.max_health += 10
            player.health = player.max_health
        elif attr == "Stamina":
            player.max_stamina += 10
            player.stamina = player.max_stamina
        elif attr == "Dexterity":
            player.dexterity += 1
        elif attr == "Strength":
            player.strength += 1
        elif attr == "Blood Shade":
            player.blood_shade += 1
        elif attr == "Sacrament":
            player.sacrament += 1

    def draw(self, screen, player, font, font_small):
        w = screen.get_width()
        h = screen.get_height()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        panel_w = 680
        panel_h = 420
        panel_x = w // 2 - panel_w // 2
        panel_y = h // 2 - panel_h // 2
        panel = pygame.Surface((panel_w, panel_h))
        panel.fill((24, 24, 24))
        screen.blit(panel, (panel_x, panel_y))
        title = font.render("Level Up", True, (255, 255, 255))
        screen.blit(title, (panel_x + 20, panel_y + 16))
        left_w = 260
        right_w = panel_w - left_w - 40
        list_x = panel_x + 20
        list_y = panel_y + 60
        sel_color = (72, 72, 72)
        for i, name in enumerate(self.attributes):
            r = pygame.Rect(list_x, list_y + i * 50, left_w, 44)
            pygame.draw.rect(screen, sel_color if i == self.selected_index else (40, 40, 40), r, 0, 6)
            t = font_small.render(name, True, (255, 255, 255))
            screen.blit(t, (r.x + 12, r.y + 10))
        vals = self.current_values(player)
        next_vals = self.next_values(player)
        attr = self.attributes[self.selected_index]
        cost = self.cost_for(player, attr)
        currency = getattr(player, "currency", 0)
        right_x = list_x + left_w + 20
        name_t = font.render(attr, True, (255, 255, 255))
        screen.blit(name_t, (right_x, list_y))
        cv = font_small.render(f"Current: {vals[attr]}", True, (220, 220, 220))
        nv = font_small.render(f"Next: {next_vals[attr]}", True, (220, 255, 220))
        cc = font_small.render(f"Cost: {cost}", True, (255, 232, 102))
        cur = font_small.render(f"Currency: {currency}", True, (144, 238, 144))
        screen.blit(cv, (right_x, list_y + 50))
        screen.blit(nv, (right_x, list_y + 90))
        screen.blit(cc, (right_x, list_y + 130))
        screen.blit(cur, (right_x, list_y + 170))
        btn_w = 180
        btn_h = 50
        confirm = pygame.Rect(right_x, panel_y + panel_h - 80, btn_w, btn_h)
        back = pygame.Rect(right_x + btn_w + 20, panel_y + panel_h - 80, btn_w, btn_h)
        can_afford = currency >= cost
        pygame.draw.rect(screen, (144, 238, 144) if can_afford else (120, 120, 120), confirm, 0, 8)
        pygame.draw.rect(screen, (255, 232, 102), back, 0, 8)
        ctext = font_small.render("Confirm", True, (0, 0, 0))
        btext = font_small.render("Back", True, (0, 0, 0))
        screen.blit(ctext, (confirm.centerx - ctext.get_width() // 2, confirm.centery - ctext.get_height() // 2))
        screen.blit(btext, (back.centerx - btext.get_width() // 2, back.centery - btext.get_height() // 2))
        hint = font_small.render("Esc to close", True, (220, 220, 220))
        screen.blit(hint, (panel_x + panel_w - hint.get_width() - 16, panel_y + 16))
        return confirm, back

    def handle_input(self, player, events, keys, confirm_btn, back_btn, toast, level_sound):
        mx, my = pygame.mouse.get_pos()
        left_mouse_pressed = pygame.mouse.get_pressed()[0]

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "close"
                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(len(self.attributes) - 1, self.selected_index + 1)
                elif event.key == pygame.K_RETURN: # Handle Enter key for selection
                    attr = self.attributes[self.selected_index]
                    cost = self.cost_for(player, attr)
                    currency = getattr(player, "currency", 0)
                    if currency >= cost:
                        self.apply_upgrade(player, attr)
                        player.currency -= cost
                        if level_sound:
                            level_sound.play()
                        toast.show("Upgrade successful.", 1200)
                    else:
                        toast.show("Not enough currency.", 1200)
            
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if confirm_btn and confirm_btn.collidepoint(mx, my):
                    attr = self.attributes[self.selected_index]
                    cost = self.cost_for(player, attr)
                    currency = getattr(player, "currency", 0)
                    if currency >= cost:
                        self.apply_upgrade(player, attr)
                        player.currency -= cost
                        if level_sound:
                            level_sound.play()
                        toast.show("Upgrade successful.", 1200)
                    else:
                        toast.show("Not enough currency.", 1200)
                elif back_btn and back_btn.collidepoint(mx, my):
                    return "back"
        return None
