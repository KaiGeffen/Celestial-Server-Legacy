from logic.Card import Card
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

class Cog(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.build(1, game, player)
cog = Cog(name="Cog", cost=0, id=2)
class Gears(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.build(2, game, player)
gears = Gears(name="Gears", cost=2, id=8)
class Factory(Card):
    def play(self, player, game, index, bonus):
        amt = game.story.get_length()
        super().play(player, game, index, bonus)
        if (amt >= 1):
            self.build(amt, game, player)
factory = Factory(name="Factory", cost=3, id=10)
class TheFuture(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.draw(1, game, player)

    def get_cost(self, player, game):
        amt = 0
        for card in game.hand[player]:
            if card.name == child.name:
                amt += card.points

        return max(self.cost - amt, 0)
the_future = TheFuture(name="The Future", cost=8, points=4, id=22)
class Generator(Card):
    def morning(self, player, game, index):
        super().build(1, game, player)
        return True
generator = Generator(name="Generator", cost=4, points=4, id=53)
class BecomeMachine(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        index = 0
        for act in game.story.acts:
            if act.owner == player:
                amt = act.card.cost
                card = Card(name=child.name, points=amt, qualities=[Quality.FLEETING], dynamic_text=f'0:{amt}, Fleeting',
                            id=child.id)
                self.transform(index, card, game)

            index += 1
become_machine = BecomeMachine(name="Become Machine", cost=1, points=0, qualities=[Quality.FLEETING], id=55)
class Anvil(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.build(2, game, player)
anvil = Anvil(name="Anvil", cost=3, points=2, id=60)
class Uprising(Card):
    def play(self, player, game, index, bonus):
        # game.sound_effect = SoundEffect.Crowd
        super().play(player, game, index, bonus + index)

    def rate_play(self, world):
        return len(world.story.acts)
uprising = Uprising(name="Uprising", cost=6, points=3, id=18)
