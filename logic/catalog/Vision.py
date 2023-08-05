from logic.Card import Card, SightCard
from logic.catalog.Tokens import seen, predator
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

class Scarab(SightCard):
    def morning(self, player, game, index):
        game.vision[player] += 1
        return True
scarab = Scarab(amt=4, name="Scarab", cost=0, points=0, id=50)
class Spy(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.create(seen, game, player ^ 1)
spy = Spy(name="Spy", cost=1, id=27)
class Awakening(Card):
    def play(self, player, game, index, bonus):
        self.add_status(1, game, player, Status.AWAKENED)

        super().play(player, game, index, bonus)
awakening = Awakening(name="Awakening", cost=3, points=3, id=39)
class Horus(Card):
    def get_cost(self, player, game):

        num_seen_cards = 0
        for i in range(len(game.story.acts)):
            act = game.story.acts[i]
            if act.owner == player ^ 1:
                if i + 1 <= game.vision[player] or Quality.VISIBLE in act.card.qualities:
                    num_seen_cards += 1

        # if game.vision[player] >= 10:
        if num_seen_cards >= 3:
            return 0
        else:
            return self.cost
horus = Horus(name="Horus", cost=7, points=7, id=45)
class Bandit(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.create(predator, game, player ^ 1)
bandit = Bandit(name="Prey", cost=1, points=2, id=26)
class Conquer(Card):
    def get_cost(self, player, game):
        num_seen_cards = 0
        for i in range(len(game.story.acts)):
            act = game.story.acts[i]
            if act.owner == player:
                num_seen_cards += 1
            else:
                if i + 1 <= game.vision[player] or Quality.VISIBLE in act.card.qualities:
                    num_seen_cards += 1

        return max(0, self.cost - num_seen_cards)
conquer = Conquer(name="Conquer", cost=5, points=3, id=67)
