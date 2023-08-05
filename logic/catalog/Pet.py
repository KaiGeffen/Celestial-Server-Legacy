from logic.Card import Card, SightCard
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

class Fruiting(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.nourish(3, game, player)
fruiting = Fruiting(name="Fruiting", cost=3, id=11)
class Oak(Card):
    def on_round_end(self, player, game):
        score_above_winning = game.score[player] - game.score[player^1]

        amt = max(0, score_above_winning)

        game.status[player].extend(amt * [Status.NOURISH])
oak = Oak(name="Oak", cost=8, points=8, id=23)
class Bounty(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for player in (0, 1):
            self.nourish(2, game, player)
bounty = Bounty(name="Bounty", cost=3, points=3, id=48)
class Bastet(Card):
    def __init__(self, points):
        text = f"2:{points}, this card retains all changes to points as it resolves (For example, if this card was nourished by 3, it stays a 2:4 once it is in the discard pile)"
        super().__init__("Bastet", cost=2, points=points, qualities=[Quality.FLEETING],
                         text=text, dynamic_text=text, id=34)

    def play(self, player, game, index, bonus):
        points = self.points + bonus
        points += game.status[player].count(Status.NOURISH)
        points -= game.status[player].count(Status.STARVE)

        bastet = Bastet(points)
        game.pile[player].append(bastet)

        super().play(player, game, index, bonus)

        # game.sound_effect = SoundEffect.Meow
bastet = Bastet(1)
class Nectar(SightCard):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.nourish(1, game, player)
nectar = Nectar(name="Nectar", amt=3, cost=1, id=25)
class Hollow(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        amt = max(0, game.score[player])

        game.score[player] = 0

        self.nourish(amt, game, player)
hollow = Hollow(name="Hollow", cost=0, points=0, id=76)
