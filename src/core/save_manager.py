import json
import os

class SaveManager:
    def __init__(self, path="save.json"):
        self.path = path

    def save(self, player):
        data = {
            "death_x": getattr(player, "death_x", 0),
            "death_y": getattr(player, "death_y", 0),
            "respawn_x": getattr(player, "respawn_x", 0),
            "respawn_y": getattr(player, "respawn_y", 0),
            "max_health": getattr(player, "max_health", 100),
            "health": getattr(player, "health", 100),
            "max_stamina": getattr(player, "max_stamina", 100),
            "stamina": getattr(player, "stamina", 100),
            "dexterity": getattr(player, "dexterity", 0),
            "strength": getattr(player, "strength", 0),
            "blood_shade": getattr(player, "blood_shade", 0),
            "sacrament": getattr(player, "sacrament", 0),
            "currency": getattr(player, "currency", getattr(player, "souls", 0)),
            "equipped": getattr(player, "equipped", {})
        }
        try:
            with open(self.path, "w") as f:
                json.dump(data, f)
        except:
            pass

    def load(self, player):
        if not os.path.exists(self.path):
            return False
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
        except:
            return False
        player.death_x = data.get("death_x", 0)
        player.death_y = data.get("death_y", 0)

        player.respawn_x = data.get("respawn_x", player.death_x)
        player.respawn_y = data.get("respawn_y", player.death_y)

        player.x = player.respawn_x
        player.y = player.respawn_y
        player.target_x = player.x
        player.target_y = player.y

        player.max_health = data.get("max_health", 100)
        player.health = data.get("health", player.max_health)
        player.max_stamina = data.get("max_stamina", 100)
        player.stamina = data.get("stamina", player.max_stamina)
        player.dexterity = data.get("dexterity", 0)
        player.strength = data.get("strength", 0)
        player.blood_shade = data.get("blood_shade", 0)
        player.sacrament = data.get("sacrament", 0)
        if hasattr(player, "currency"):
            player.currency = data.get("currency", 0)
        elif hasattr(player, "souls"):
            player.souls = data.get("currency", 0)
        player.equipped = data.get("equipped", {})
        return True
