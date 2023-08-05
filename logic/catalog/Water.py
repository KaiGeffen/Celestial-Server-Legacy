from logic.Card import Card
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

class Gift(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for player in (0, 1):
            self.draw(1, game, player)

    def rate_play(self, world):
        return 3 + len(world.opp_hand)/2 - len(world.hand)/2
gift = Gift(name="Gift", cost=3, points=3, id=12)

class Icarus(Card):
    def get_cost(self, player, game):
        amt = 0

        if not game.story.is_empty():
            for act in game.story.acts:
                if act.owner == player:
                    amt += 1

        if amt == 4:
            return 0
        else:
            return self.cost
icarus = Icarus(name="Icarus", cost=7, points=7, id=46)
class FishingBoat(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for i in range(3):
            self.tutor(1, game, player)
fishing_boat = FishingBoat(name="Fishing Boat", cost=2, points=1, id=32)
class Drown(Card):
    def play(self, player, game, index, bonus):
        # game.sound_effect = SoundEffect.Drown
        super().play(player, game, index, bonus)
        self.mill(3, game, player)
drown = Drown(name="Drown", cost=1, points=1, id=5)
class PocketWatch(Card):
    def get_cost(self, player, game):
        cost = max(0, self.cost - game.amt_passes[player])
        return cost

    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.draw(2, game, player)
pocket_watch = PocketWatch(name="Pocket Watch", cost=4, points=2, id=54)
class Axolotl(Card):
    def morning(self, player, game, index):
        super().create(axolotl, game, player)
        return True
axolotl = Axolotl(name="Axolotl", cost=1, points=1, id=63)
class GentleRain(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        amt = game.amt_drawn[player]

        self.nourish(amt, game, player)
gentle_rain = GentleRain(name="Gentle Rain", cost=4, points=2, id=71)
