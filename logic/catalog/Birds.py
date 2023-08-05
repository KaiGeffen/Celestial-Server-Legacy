from logic.Card import Card
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

class Dove(Card):
    def play(self, player, game, index, bonus):
        # game.sound_effect = SoundEffect.Bird
        super().play(player, game, index, bonus)
dove = Dove(name="Dove", cost=1, points=1, qualities=[Quality.VISIBLE, Quality.FLEETING], id=4)
class Swift(Card):
    def play(self, player, game, index, bonus):
        if not game.story.is_empty():
            if game.story.acts[0].card.cost == 1:
                bonus += 1

        super().play(player, game, index, bonus)
    def rate_play(self, world):
        value = 2
        # TODO
        return value
swift = Swift(name="Swift", cost=2, points=2, qualities=[Quality.VISIBLE, Quality.FLEETING], id=7)
class Pelican(Card):
    def play(self, player, game, index, bonus):
        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        super().play(player, game, index, bonus + amt)
        self.oust(amt, game, player)
pelican = Pelican(name="Pelican", cost=4, points=4, id=40, qualities=[Quality.VISIBLE])
class Phoenix(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.create(dove, game, player)
phoenix = Phoenix(name="Phoenix", cost=5, points=5, qualities=[Quality.VISIBLE, Quality.FLEETING], id=51)
class Heron(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.reset(game)

    def get_cost(self, player, game):
        return self.cost + len(game.pile[player])

    def rate_play(self, world):
        return self.rate_reset(world)
heron = Heron(name="Heron", cost=1, points=0, id=65, qualities=[Quality.VISIBLE])
