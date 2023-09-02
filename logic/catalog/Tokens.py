from logic.Card import Card
from logic.Effects import Quality

class Seen(Card):
    def on_upkeep(self, player, game, index):
        game.vision[player ^ 1] += 4
        return True
seen = Seen(name="Seen", cost=2, qualities=[Quality.FLEETING], id=1001)
class Ashes(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.draw(1, game, player)
ashes = Ashes(name="Ashes", cost=1, qualities=[Quality.FLEETING], id=1002)
child = Card(name='Child', qualities=[Quality.FLEETING], id=1003)
class Predator(Card):
    def play(self, player, game, index, bonus):
        # NOTE This name must match the name of the card that creates it
        bonus += sum(2 for card in game.pile[player ^ 1] if card.name == 'Prey')

        super().play(player, game, index, bonus)
predator = Predator(name="Predator", cost=1, qualities=[Quality.FLEETING], id=1004)

tokens = [seen, ashes, child, predator]