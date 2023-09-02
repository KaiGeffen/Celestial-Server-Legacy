from logic.Card import Card, CardCodec
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

class Dagger(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        super().play(player, game, index, bonus)
        self.discard(1, game, opp)

        # game.sound_effect = SoundEffect.Cut

    def rate_play(self, world):
        return self.rate_discard(world)
dagger = Dagger(name="Dagger", cost=1, id=1)
class Shadow(Card):
    def get_cost(self, player, game):
        opp = (player + 1) % 2

        return len(game.hand[opp])

    def rate_delay(self, world):
        return 10
shadow = Shadow(name="Shadow", cost=6, points=3, id=19)
class Imprison(Card):
    def on_round_end(self, player, game):
        # If opponent had 3 or fewer points
        if game.score[player^1] <= 3:
            # Give them Nourish -1
            game.status[player^1].extend([Status.STARVE])
imprison = Imprison(name="Imprison", cost=3, points=3, id=35)
class Nightmare(Card):
    def morning(self, player, game, index):
        if len(game.hand[player^1]) < len(game.hand[player]):
            super().create(shadow, game, player)
            return True
nightmare = Nightmare(name="Nightmare", cost=2, points=2, id=68)
class Boa(Card):
    def play(self, player, game, index, bonus):
        nourished = (Status.NOURISH in game.status[player]) or (Status.STARVE in game.status[player])
        super().play(player, game, index, bonus)
        if nourished:
            super().discard(1, game, player^1)

    def rate_play(self, world):
        nourished = (Status.NOURISH in world.status) or (Status.STARVE in world.status)

        if nourished:
            return self.points + self.rate_discard(world)
        else:
            return self.points
boa = Boa(name="Boa", cost=6, points=6, id=57)
class HungryGhost(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.starve(4, game, player)

    def rate_delay(self, world):
        return 12
hungry_ghost = HungryGhost(name="Hungry Ghost", cost=2, points=4, id=31)
class Hurricane(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.reset(game)

    def rate_play(self, world):
        return self.rate_reset(world)
hurricane = Hurricane(name="Hurricane", cost=4, id=13)
class WingClipping(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        if game.hand[player^1]:
            card = game.hand[player^1].pop(0)
            game.deck[player^1].append(card)

            game.animations[player^1].append(
                Animation('Hand', 'Deck', card=CardCodec.encode_card(card)))

    def rate_play(self, world):
        return self.points + self.rate_discard(world)
wing_clipping = WingClipping(name="Wing Clipping", cost=5, points=3, id=16)
class Sickness(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.starve(4, game, player ^ 1)
        self.create(sickness, game, player ^ 1)
sickness = Sickness(name="Sickness", cost=3, points=-1, qualities=[Quality.FLEETING], id=58)
