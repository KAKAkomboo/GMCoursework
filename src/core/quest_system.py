import random

class Quest:
    def __init__(self, title, description, reward=0):
        self.title = title
        self.description = description
        self.reward = reward
        self.completed = False

class QuestSystem:
    def __init__(self):
        self.active_quests = []
        self.quest_pool = [
            Quest("Знайди загублений годинник", "Хтось загубив годинник біля старого мосту.", 50),
            Quest("Полювання на щурів", "Вбий 5 щурів у підвалі.", 30),
            Quest("Доставка ліків", "Віднеси ліки старому на околиці.", 40),
            Quest("Збір трав", "Збери 3 цілющі трави в лісі.", 25)
        ]

    def get_random_quest(self):
        available = [q for q in self.quest_pool if q not in self.active_quests and not q.completed]
        if available:
            quest = random.choice(available)
            self.active_quests.append(quest)
            return quest
        return None

    def complete_quest(self, title):
        for quest in self.active_quests:
            if quest.title == title:
                quest.completed = True
                self.active_quests.remove(quest)
                return quest
        return None
