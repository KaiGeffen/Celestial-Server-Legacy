from logic.Card import *
from logic.catalog.Birds import *
from logic.catalog.Ashes import *
from logic.catalog.Pet import *
from logic.catalog.Shadow import *
from logic.catalog.Birth import *
from logic.catalog.Vision import *
from logic.catalog.Stars import *
from logic.catalog.Water import *
from logic.catalog.Tokens import tokens

from logic.Effects import Status, Quality
from logic.Story import Source
from Animation import Animation

"""Other"""
class Paramountcy(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        # Up to the number of spaces left(99), pop from discard pile and add to story
        space = 99 - (index + 1 + len(game.story.acts))
        for i in range(min(space, 5)):
            if game.pile[player]:
                card = game.pile[player].pop()
                game.story.add_act(card, player, Source.PILE, i)

                # story_index = len(game.story.acts) - 1
                game.animations[player].append(Animation('Discard', 'Story', index2=i))
paramountcy = Paramountcy(name="Paramountcy", cost=9, points=0, id=62)

""" DEV CARDS """
class Rat(Card):
    def play(self, player, game, index, bonus):
        if game.mana[player] >= 2:
            game.mana[player] -= 2
            for act in game.story.acts:
                if act.owner == player:
                    bonus += 1

        super().play(player, game, index, bonus)

        if len(game.hand[player]) == 0:
            self.draw(1, game, player)
rat = Rat(name="Rat", cost=0, points=0, id=2000)
class Beggar(Card):
    def play(self, player, game, index, bonus):
        if len(game.story.acts) > 0:
            cost = game.story.acts[0].card.cost
            self.tutor(cost, game, player)

        if game.mana[player] >= 1:
            game.mana[player] -= 1
            bonus += 1

        super().play(player, game, index, bonus)
beggar = Beggar(name="Beggar", cost=0, points=0, id=2001)
class FreshAir(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        game.mana[player] += 3

        if all(act.owner != player for act in game.story.acts):
            self.draw(1, game, player)
fresh_air = FreshAir(name="FreshAir", cost=2, points=1, id=2002)
class Possibilities(Card):
    def play(self, player, game, index, bonus):
        double = False
        if game.mana[player] >= 4:
            game.mana[player] -= 4
            double = True

        if game.mana[player] >= 1:
            game.mana[player] -= 1
            bonus += 1
        if game.mana[player] >= 2:
            game.mana[player] -= 2
            bonus += 2

        if double:
            bonus += bonus + self.points + game.score[player]

        super().play(player, game, index, bonus)
possibilities = Possibilities(name="Possibilities", cost=2, points=2, id=2003)
class Hatchling(Card):
    def __init__(self, points):
        text = f'0:{points}'
        super().__init__("Hatchling", dynamic_text=text, cost=0, points=points, id=2004)

    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        if game.mana[player] >= 2:
            game.mana[player] -= 2

            for _ in range(2):
                card = dove
                game.story.add_act(card, player)

                story_index = len(game.story.acts) + index - 1
                game.animations[player].append(Animation('Gone', 'Story', index2=story_index))
    def morning(self, player, game, index):
        new_card = Hatchling(self.points + 1)

        # Has a bug if moon is triggering this, since it pops the top card instead of _index_
        game.pile[player].pop()
        super().create_in_pile(new_card, game, player)

        # Remove the creation animation
        game.animations = [[], []]

        return True
hatchling = Hatchling(0)
class Eyes(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.draw(1, game, player)
    def in_hand_on_play(self, player, game):
        game.vision[player] += 1
        return True
eyes = Eyes(name="Eyes", cost=1, id=2005)
class Capybara(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        if game.mana[player] >= 1:
            game.mana[player] -= 1
            self.draw(1, game, player)
        if game.mana[player] >= 4:
            game.mana[player] -= 4
            self.reset(game)
capybara = Capybara(name="Capybara", cost=0, points=0, id=2006)
class Rekindle(Card):
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
rekindle = Rekindle(name="Rekindle", cost=3, points=2, id=2007)
class Tragedy(Card):
    def play(self, player, game, index, bonus):
        if len(game.story.acts) == 0:
            bonus += 2

        super().play(player, game, index, bonus)

        for i in range(len(game.story.acts)):
            act = game.story.acts[i]
            if act.card.cost <= 2:
                self.remove_act(i, game)
                return
tragedy = Tragedy(name="Tragedy", cost=0, points=1, id=2008)
class Hound(Card):
    def get_cost(self, player, game):
        if len(game.story.acts) > 0:

            card = game.story.acts[-1].card

            for (yesterday_card, _, _) in game.recap.story:
                if yesterday_card.name == card.name:
                    return 1

        return self.cost
hound = Hound(name="Hound", cost=2, points=2, id=2009)
class Lullaby(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for act in game.story.acts:
            card = act.card
            if card.cost == 0:
                self.create(card, game, player)
lullaby = Lullaby(name="Lullaby", cost=6, points=4, id=2010)
class Longing(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        # For each card in our pile, if it's even-costed, move it atop the deck
        for i in range(len(game.pile[player]) - 1, -1, -1):
            card = game.pile[player][i]
            if card.cost % 2 == 0:
                game.pile[player].pop(i)
                game.deck[player].append(card)

                # Add an animation of card going from pile to deck
                game.animations[player].append(
                    Animation('Discard', 'Deck', card=CardCodec.encode_card(card)))

        # Shuffle the deck (Don't shuffle the full discard pile into it)
        game.shuffle(player, remember=False, take_pile=False)

        if game.mana[player] >= 4:
            game.mana[player] -= 4
            self.nourish(5, game, player)
longing = Longing(name="Longing", cost=1, points=0, id=2011)
class Dwindle(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        self.inspire(2, game, player)

        if game.mana[player] >= 3:
            game.mana[player] -= 3
            self.reset(game)

        if game.mana[player] >= 2:
            game.mana[player] -= 2
            self.draw(1, game, player)
dwindle = Dwindle(name="Dwindle", cost=2, points=0, id=2012)
class Cloud(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        self.draw(1, game, player)

    def morning(self, player, game, index):
        if len(game.hand[player]) == 6:
            game.status[player].append(Status.UNLOCKED)

        return True
cloud = Cloud(name="Cloud", cost=3, points=0, id=2013)

"""Lists"""
hidden_card = Card(name="Cardback", cost=0, points=0, id=1000)
full_catalog = [
    stars, dagger, nascence, impulse, dove, drown, dash, swift,
    birth, cosmos, ancestry, fruit, mercy, hurricane, aronist, mine,
    wing_clipping, veteran, uprising, shadow, cling, death, the_future, oak,

    nectar, prey, clear_view, night_vision, hungry_ghost,
    fishing_boat, hold_tight, pet, imprison, awakening,
    secretary_bird, ecology, enlightenment, excess,

    bounty, dawn, phoenix, generator, iceberg, rebirth, sun,
    boa,
    sickness, cradle,
    paramountcy, dew, parch, heron,
    conquer, nightmare, from_ashes, gentle_rain, sunflower, hollow, moon,

    rat, beggar, fresh_air, possibilities, hatchling, eyes, capybara,
    rekindle, tragedy, hound, lullaby, longing, dwindle,

    cloud,
    ]

non_collectibles = [hidden_card] + tokens
all_cards = full_catalog + non_collectibles


common_cards = list(filter(lambda card: card.rarity == 0, full_catalog))
uncommon_cards = list(filter(lambda card: card.rarity == 1, full_catalog))
rare_cards = list(filter(lambda card: card.rarity == 2, full_catalog))
legend_cards = list(filter(lambda card: card.rarity == 3, full_catalog))


import random
# Get a random deck for the computer opponent
def get_computer_deck(i = None):
    # Not too strong, aiming for C tier core set decks
    # 2 each of anubis, aggro, uprising, oak, stalker

    # New deck using web-app cards:
    possible_decks = [
        [
            # Standard anubis
            impulse, impulse, impulse, drown, drown,
            swift, swift, dash,
            mercy, fruit,
            aronist, aronist,
            veteran, veteran,
            death,
        ], [
            # All in anubis
            stars, stars,
            impulse, impulse, drown, drown, drown,
            aronist, aronist, aronist, aronist,
            veteran,
            cling,
            death, death,
        ], [
            # Aggro Anubis
            stars,
            impulse, impulse, impulse, impulse, impulse,
            dash, dash, swift, swift,
            mercy, mercy,
            mine, mine,
            death
        ], [
            # Standard oak
            stars, stars, stars,
            dove, dove, dove,
            cosmos, swift,
            mercy, mercy, fruit, fruit,
            aronist,
            death,
            oak,
        ], [
            # Sarco oak
            stars, stars, stars,
            dove, drown, drown,
            cosmos, birth,
            mercy, fruit,
            shadow, uprising, cling, cling,
            oak,
        ], [
            # Uprising
            nascence, nascence,
            dove, dove, impulse,
            birth, birth, birth, swift, dash,
            mercy, mercy, mercy,
            uprising, uprising,
        ], [
            # Uprising + Factory
            nascence, nascence, nascence,
            dove, dove, dove, impulse,
            cosmos, swift, dash,
            ancestry, mercy, mercy,
            uprising, shadow,
        ], [
            # Aggro
            stars,
            dove, impulse, impulse, impulse, impulse,
            birth, swift, swift, dash, dash,
            mercy, mercy, mercy,
            mine,
        ], [
            # Bad stalker
            stars, stars,
            dove, dove, dove,
            swift, swift,
            fruit, fruit,
            wing_clipping, wing_clipping, wing_clipping,
            shadow, shadow, cling,
        ], [
            # Stalker oak
            stars, stars, stars,
            dove, dove, dove,
            cosmos,
            fruit, fruit,
            wing_clipping, wing_clipping, wing_clipping,
            shadow, shadow, cling,
            oak
        ], [
            # Aggro to late hyperthin
            dove, dove, dove, dove, dove, dove,
            dash, dash,
            mercy, mercy, mercy,
            aronist, aronist,
            oak, oak,
        ]
    ]

    if i is not None:
        try:
            return possible_decks[i]
        except:
            print('Invalid ai deck: ' + i)

    return random.choice(possible_decks)
