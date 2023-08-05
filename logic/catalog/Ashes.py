from logic.Card import *
from logic.catalog.Tokens import ashes
from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

dash = FireCard(name="Dash", cost=2, points=3, id=6)
class CrossedBones(Card):
    def play(self, player, game, index, bonus):
        # game.sound_effect = SoundEffect.Fire

        super().play(player, game, index, bonus)

        for _ in range(2):
            self.create_in_pile(ashes, game, player)
crossed_bones = CrossedBones(name="Crossed Bones", cost=1, points=1, qualities=[Quality.FLEETING], id=3)
class Mine(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        self.dig(4, game, player)
mine = Mine(name="Mine", cost=4, points=4, id=15)
class DinosaurBones(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for _ in range(3):
            self.create_in_pile(ashes, game, player)
dinosaur_bones = DinosaurBones(name="Dinosaur Bones", cost=4, points=4, qualities=[Quality.FLEETING], id=14)
class Parch(Card):
    def play(self, player, game, index, bonus):
        for act in game.story.acts:
            if act.owner == player:
                bonus += 1

        super().play(player, game, index, bonus)

        i = 0
        while i < len(game.story.acts):
            act = game.story.acts[i]
            if act.owner == player:
                self.remove_act(i, game)
            else:
                i += 1
    def on_play(self, player, game):
        game.status[player].append(Status.UNLOCKED)
parch = Parch(name="Parch", cost=3, points=2, id=64)
class Unearth(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        if game.pile[player]:
            card = game.pile[player].pop()
            game.deck[player].append(card)

            game.animations[player].append(
                Animation('Discard', 'Deck', card=CardCodec.encode_card(card)))
unearth = Unearth(name="Unearth", cost=2, points=2, id=33)
class Tumulus(Card):
    def play(self, player, game, index, bonus):
        if len(game.pile[player]) >= 8:
            bonus += 2

        super().play(player, game, index, bonus)

    def rate_play(self, world):
        pile_has_8 = len(world.pile[0]) # TODO Cards in story
        return 4 + 2 * pile_has_8
tumulus = Tumulus(name="Tumulus", cost=5, points=4, id=17)
class Sarcophagus(Card):
    def play(self, player, game, index, bonus):
        highest_cost = -1
        highest_index = None
        for pile_index in range(len(game.pile[player])):
            card = game.pile[player][pile_index]

            if card.cost > highest_cost:
                highest_cost = card.cost
                highest_index = pile_index

        if highest_index is not None:
            card = game.pile[player].pop(highest_index)
            game.deck[player].append(card)

            bonus += highest_cost

            # game.sound_effect = SoundEffect.Sarcophagus
            game.animations[player].append(
                Animation('Discard', 'Deck', card=CardCodec.encode_card(card)))

            super().play(player, game, index, bonus)
        else:
            super().play(player, game, index, bonus)

    def rate_play(self, world):
        highest_cost = 0
        for card in world.pile[0]:
            highest_cost = max(highest_cost, card.cost)

        for act in world.story.acts:
            if act.owner == 0:
                highest_cost = max(highest_cost, act.card.cost)

        # Account for the value of getting a high value card back
        if highest_cost <= 3:
            return highest_cost - 1
        elif highest_cost <= 5:
            return highest_cost
        else:
            return highest_cost + 1
sarcophagus = Sarcophagus(name="Sarcophagus", cost=6, id=20)
class Anubis(Card):
    def get_cost(self, player, game):
        if len(game.pile[player]) >= 12:
            return 0
        else:
            return self.cost
anubis = Anubis(name="Anubis", cost=7, points=7, id=21)
class Carrion(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        # Nourish amount is the number of Fleeting cards in the top 3 of the discard pile
        amt = sum(Quality.FLEETING in card.qualities for card in game.pile[player][-3:])

        # Remove the top 3 cards of discard pile from the game
        self.dig(3, game, player)

        self.nourish(amt, game, player)
carrion = Carrion(name="Carrion", cost=2, points=1, id=74)
