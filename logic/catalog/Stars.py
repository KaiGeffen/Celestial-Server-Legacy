from logic.Card import Card, SightCard, CardCodec
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

class Stars(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.inspire(1, game, player)
stars = Stars(name="Stars", id=0)
class Cosmos(Card):
    def play(self, player, game, index, bonus):
        amt = 1
        for act in game.story.acts:
            if act.owner == player:
                amt += 1
        super().play(player, game, index, bonus)
        self.inspire(amt, game, player)
cosmos = Cosmos(name="Cosmos", cost=2, id=9)
class NightVision(SightCard):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.tutor(2, game, player)
night_vision = NightVision(amt=3, name="Night Vision", cost=1, points=0, id=28)
class Ecology(Card):
    def on_play(self, player, game):
        game.mana[player] += 10
ecology = Ecology(name="Ecology", cost=7, points=0, id=44)
class Sun(Card):
    def morning(self, player, game, index):
        super().add_mana(2, game, player)
        return True
sun = Sun(name="Sun", cost=8, points=8, id=56)
class Moon(Card):
    def morning(self, player, game, index):
        # Iterate through each card below this, trigger its morning effect
        # Stop after 2 effects have been triggered
        count = 0
        for i in range(index - 1, -1, -1):
            if (count >= 2):
                break

            card = game.pile[player][i]
            if card.morning(player, game, i):
                # Add an animation for the card
                game.animations[player].append(
                    Animation('Discard', 'Discard', CardCodec.encode_card(card), index=i, index2=i))

                count += 1

        return True
moon = Moon(name="Moon", cost=5, points=4, id=73)
class Sunflower(Card):
    def play(self, player, game, index, bonus):
        points = self.points + bonus
        points += game.status[player].count(Status.NOURISH)
        points -= game.status[player].count(Status.STARVE)

        super().play(player, game, index, bonus)

        self.inspire(points, game, player)
sunflower = Sunflower(name="Sunflower", cost=2, points=1, id=69)
