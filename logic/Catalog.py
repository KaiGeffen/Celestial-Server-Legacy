import CardCodec
from logic.Card import *
from logic.Effects import Status, Quality
from logic.Story import Source, Act
import Animation

# TODO make a separate file for tokens
"""Tokens"""
class Camera(Card):
    def on_upkeep(self, player, game, index):
        game.vision[player ^ 1] += 4
camera = Camera(name="Camera", cost=2, qualities=[Quality.FLEETING],
                text="2:0, Fleeting, at the start of each round, give your opponent vision 4")
class BrokenBone(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.BoneSnap
        return super().play(player, game, index, bonus)
broken_bone = BrokenBone(name="Broken Bone", cost=1, qualities=[Quality.FLEETING], text="1:0, Fleeting")
robot = Card(name='Robot', qualities=[Quality.FLEETING], text="0:X, Fleeting")
class WantedPoster(Card):
    def play(self, player, game, index, bonus):
        bonus += 2 * game.pile[player ^ 1].count(bandit)

        return super().play(player, game, index, bonus)
wanted_poster = WantedPoster(name="Wanted Poster", cost=1, qualities=[Quality.FLEETING],
                             text="1:0, fleeting, +2 for each Bandit in your opponent's discard pile")

tokens = [camera, broken_bone, robot, wanted_poster]

"""FIRE"""
dash = FireCard(name="Dash", cost=2, points=3, text="2:3, flare (Worth 1 less for every card before it)")
class Enrage(Card):
    def on_play(self, player, game):
        for act in game.story.acts:
            act.bonus -= act.card.cost

    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus) + '\nOppress'

        for act in game.story.acts:
            act.bonus -= act.card.cost

        game.sound_effect = SoundEffect.Yell
        return recap
enrage = Enrage(name="Enrage", cost=8, points=2,
                text="8:2, give each card later in the story -X, where X is its cost.\nWhen played, give each card ealier in the story -X.")

"""BIRD"""
class Dove(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.Bird
        return super().play(player, game, index, bonus)
dove = Dove(name="Dove", cost=1, points=1, qualities=[Quality.VISIBLE, Quality.FLEETING],
            text="1:1, visible, fleeting (After resolving, this card is removed from the game instead of moving to your discard pile)")
class Swift(Card):
    def play(self, player, game, index, bonus):
        if not game.story.is_empty():
            if game.story.acts[0].card.cost == 1:
                bonus += 1

        return super().play(player, game, index, bonus)
swift = Swift(name="Swift", cost=2, points=2, qualities=[Quality.VISIBLE],
              text="2:2, visible, if the next card costs 1, +1")
class Pelican(Card):
    def play(self, player, game, index, bonus):
        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        recap = super().play(player, game, index, bonus + amt)
        recap += self.oust(amt, game, player)

        return recap
pelican = Pelican(name="Pelican", cost=4, points=4, text="4:4, oust each 0 or 1 cost card from your hand, +1 for each")
class Icarus(Card):
    def get_cost(self, player, game):
        amt = 0

        if not game.story.is_empty():
            for act in game.story.acts:
                if act.owner == player:
                    amt += 1

        if amt == 5:
            return 0
        else:
            return self.cost
icarus = Icarus(name="Icarus", cost=7, points=7, text="7:7, costs 0 if you have 5 cards in story")
class Eagle(SightCard):
    def on_play(self, player, game):
        game.hand[player] = [dove] * len(game.hand[player])

        super().on_play(player, game)

    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(2, game, player)
eagle = Eagle(amt=4, name="Eagle", cost=6, points=6,
                    text="6:6, nourish 2. When played, gain sight 4 and transform each card in your hand into a Dove.")

"""Discard"""
class BoneKnife(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(1, game, opp)
bone_knife = BoneKnife(name="Bone Knife", text="0:0, opponent discards 1")
class Stalker(Card):
    def get_cost(self, player, game):
        opp = (player + 1) % 2

        return len(game.hand[opp])
stalker = Stalker(name="Stalker", cost=6, points=4, text="X:4, X is cards in opponent's hand")
class Imprison(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        recap = super().play(player, game, index, bonus)
        recap += self.reset(game)

        game.score[opp] = len(game.hand[opp])
        recap += f'\n+{len(game.hand[opp])} opp'

        return recap
imprison = Imprison(name="Imprison", cost=2, text="2:0, reset, then give opponent 1 point for each card in their hand")
class Gift(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for player in (0, 1):
            recap += self.draw(1, game, player)

        return recap
gift = Gift(name="Gift", cost=3, points=3, text="3:3, both players draw 1")

"""Machines"""
class Cog(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(1, game, player)
cog = Cog(name="Cog", cost=0, text="0:0, build 1 (+1 to a robot in your hand, or make a 0:1 fleeting robot)")
class Gears(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(2, game, player)
gears = Gears(name="Gears", cost=2, text="2:0, build 2")
class Factory(Card):
    def play(self, player, game, index, bonus):
        amt = game.story.get_length()
        return super().play(player, game, index, bonus) + self.build(amt, game, player)
factory = Factory(name="Factory", cost=3, text="3:0, build X, where X is number of cards later in the story")
class AI(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.draw(1, game, player)
        return recap

    def get_cost(self, player, game):
        amt = 0
        for card in game.hand[player]:
            if card.name == 'Robot':
                amt += card.points

        return max(self.cost - amt, 0)
ai = AI(name="AI", cost=8, points=4, text="8:4, draw 1. Costs X less where X is total robot points in hand")
class Sine(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.starve(4, game, player)
sine = Sine(name="Sine", cost=2, points=4, text="2:4, starve 4 (Your next card gives -4 points)")

"""Nature"""
class Stars(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.inspire(1, game, player)
stars = Stars(name="Stars", text="0:0, inspire (Next turn gain 1 temporary mana)")
class Cosmos(Card):
    def play(self, player, game, index, bonus):
        amt = 1
        for act in game.story.acts:
            if act.owner == player:
                amt += 1
        return super().play(player, game, index, bonus) + self.inspire(amt, game, player)
cosmos = Cosmos(name="Cosmos", cost=2, text="2:0, inspire 1 + 1 for each card you play later this round")
class Fruiting(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(3, game, player)
fruiting = Fruiting(name="Fruiting", cost=3, text="3:0, nourish 3 (Your next card gives +3 points)")
class Lotus(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.inspire(2, game, player)

        if self.your_final(game, player):
            recap += self.reset(game)

        return recap
lotus = Lotus(name="Lotus", cost=5, text="5:0, inspire 2, final: reset")
class Oak(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.gentle(game, player)
oak = Oak(name="Oak", cost=8, points=8,
          text="8:8, gentle (If you win this round, convert to nourish any points not needed to win)")

"""Earth"""
class CrossedBones(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += '\nBury:'
        for _ in range(2):
            recap += self.create_in_pile(broken_bone, game, player)

        return recap
crossed_bones = CrossedBones(name="Crossed Bones", cost=1, points=2, qualities=[Quality.FLEETING],
                             text="1:2, becomes 2x 1:0 fleeting broken bones after resolving")
class Mine(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.dig(4, game, player)

        return recap
mine = Mine(name="Mine", cost=4, points=4, text="4:4, oust the top 4 cards of your discard pile")
class DinosaurBones(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += '\nBury:'
        for _ in range(3):
            recap += self.create_in_pile(broken_bone, game, player)

        return recap
dinosaur_bones = DinosaurBones(name="Dinosaur Bones", cost=4, points=5, qualities=[Quality.FLEETING],
                               text="4:5, becomes 3x 1:0 fleeting broken bones after resolving")
class Bastet(Card):
    def __init__(self, points):
        text = f"2:{points}, this card retains all changes to points as it resolves (For example, if this card was nourished by 3, it stays a 2:4 once it is in the discard pile)"
        super().__init__("Bastet", cost=2, points=points, qualities=[Quality.FLEETING],
                         text=text, dynamic_text=text)

    def play(self, player, game, index, bonus):
        points = self.points + bonus
        points += game.status[player].count(Status.NOURISH)
        points -= game.status[player].count(Status.STARVE)

        bastet = Bastet(points)
        game.pile[player].append(bastet)

        recap = super().play(player, game, index, bonus)

        game.sound_effect = SoundEffect.Meow
        return recap
bastet = Bastet(1)
class NightVision(SightCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(2, game, player)

        return recap
night_vision = NightVision(amt=3, name="Night Vision", cost=1, points=0, text="1:0, tutor 2. On play, sight 3")

"""Ships"""
class FishingBoat(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for i in range(3):
            recap += self.tutor(1, game, player)

        return recap
fishing_boat = FishingBoat(name="Fishing Boat", cost=2, text="2:0, tutor a 1 3 times")

"""Death"""
class Drown(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.Drown
        return super().play(player, game, index, bonus) + self.mill(3, game, player)
drown = Drown(name="Drown", cost=1, points=1, text="1:1, mill yourself 3 (Top 3 cards of deck go to pile)")
class RaiseDead(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if game.pile[player]:
            card = game.pile[player].pop()
            game.deck[player].append(card)

            recap += f'\nRaise {card.name}'
            game.animations[player].append(('Discard', 'Deck', CardCodec.encode_card(card)))

        return recap
raise_dead = RaiseDead(name="Raise Dead", cost=2, points=2, text="2:2 put the top card of your pile on top of deck")
class Tumulus(Card):
    def play(self, player, game, index, bonus):
        if len(game.pile[player]) >= 8:
            bonus += 2

        return super().play(player, game, index, bonus)
tumulus = Tumulus(name="Tumulus", cost=5, points=4, text="5:4, +2 if your pile has at least 8 cards in it")
class Sarcophagus(Card):
    def play(self, player, game, index, bonus):
        recap = ''

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

            game.sound_effect = SoundEffect.Sarcophagus
            game.animations[player].append(('Discard', 'Deck', CardCodec.encode_card(card)))


            return super().play(player, game, index, bonus) + f"\nTop: {card.name}"
        else:
            return super().play(player, game, index, bonus)
sarcophagus = Sarcophagus(name="Sarcophagus", cost=6,
                          text="6:X, put the highest cost card from your pile on top of your deck, X is its cost")
class Anubis(Card):
    def get_cost(self, player, game):
        if len(game.pile[player]) >= 12:
            return 0
        else:
            return self.cost
anubis = Anubis(name="Anubis", cost=7, points=7, text="7:7, costs 0 if you have at least 12 cards in your pile")
class Crypt(Card):
    def play(self, player, game, index, bonus):
        result = super().play(player, game, index, bonus)

        index_final_owned_card = -1
        final_card = None
        index = 0
        for act in game.story.acts:
            if act.owner == player and act.source != Source.SPRING:
                index_final_owned_card = index
                final_card = act.card

            index += 1

        if final_card is not None:
            # The card from pile to replace the final card with
            replacement_card = None

            for card in game.pile[player][::-1]:
                if card.cost == final_card.cost:
                    replacement_card = card
                    break

            if replacement_card is not None:
                # The full act with which to replace player's final act
                replacement_act = Act(card=replacement_card,
                                      owner=player,
                                      source=Source.PILE)

                game.story.replace_act(index_final_owned_card, replacement_act)

                result += f'\n{replacement_card.name} replaced {final_card.name}'

        return result
crypt = Crypt(name="Crypt", cost=2, points=2,
              text="2:2, your last unsprung card this round transforms into the first card in your pile with the same cost as it")

"""INSECTS"""
bee = Card(name="Bee", cost=0, points=1, qualities=[Quality.VISIBLE], text="0:1, visible")
class Nectar(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(1, game, player)
nectar = Nectar(name="Nectar", cost=1, text="1:0, nourish 1 (Your next card gives +1 points)")
class Beekeep(Card):
    def __init__(self, stored=None):
        self.stored = stored

        name = "Beekeep"
        cost = 5
        points = 5

        stats = f"{cost}:{points}"
        text = f"{stats}, remove from the game and note all 0-cost cards in your discard pile. This card's effect becomes to add to your discard pile a copy of each of the noted cards."

        if stored:
            converted_list = [card.name for card in stored]
            joined_string = ", ".join(converted_list)

            dynamic_text = f"{stats}, add a copy of each of these cards to your discard pile:\n{joined_string}"
            qualities = []
        else:
            dynamic_text = ""
            qualities = [Quality.FLEETING]

        super().__init__(name=name, cost=cost, points=points, qualities=qualities, text=text, dynamic_text=dynamic_text)

    def play(self, player, game, index, bonus):
        if self.stored:
            recap = super().play(player, game, index, bonus)

            for card in self.stored:
                recap += self.create_in_pile(card, game, player)

            return recap

        else:
            cards = []
            card_names = []
            for card in game.pile[player]:
                if card.cost == 0:
                    cards.append(card)
                    card_names.append(card.name)

            # Remove from pile all 0 cost cards
            game.pile[player] = list(filter(lambda card: card.cost != 0, game.pile[player]))

            new_beekeep = Beekeep(stored=cards)
            self.create_in_pile(new_beekeep, game, player)

            # Form the recap
            recap = super().play(player, game, index, bonus)
            if cards:
                recap += "\nStored: " + "\n".join(card_names)

            return recap
beekeep = Beekeep()

"""Other"""
class Hurricane(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.reset(game)
hurricane = Hurricane(name="Hurricane", cost=4, text="4:0, reset")
class Spy(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(camera, game, player ^ 1)
spy = Spy(name="Spy", cost=1, text="1:0, create a 2:0 camera in opponent's hand which gives you sight each upkeep")
class Stable(Card):
    def __init__(self, stored=None):
        self.stored = stored

        name = "Stable"
        cost = 3
        points = 3

        stats = f"{cost}:{points}"
        text = f"{stats}, remove from the game and note the top card of your discard pile. This card's effect becomes to add a copy of the noted card to your hand."

        if stored:
            dynamic_text = f"{stats}, add a copy of {stored.name} to your hand"
            if stored.dynamic_text:
                dynamic_text += f" ({stored.dynamic_text})"
            else:
                dynamic_text += f" ({stored.text})"
            qualities = []
        else:
            dynamic_text = ""
            qualities = [Quality.FLEETING]

        super().__init__(name=name, cost=cost, points=points, qualities=qualities, text=text, dynamic_text=dynamic_text)

    def play(self, player, game, index, bonus):
        if self.stored:
            return super().play(player, game, index, bonus) + self.create(self.stored, game, player)

        else:
            card = None
            if game.pile[player]:
                card = game.pile[player].pop()

            if card is not None:
                new_stable = Stable(stored=card)
                game.pile[player].append(new_stable)

                return super().play(player, game, index, bonus) + f"\nStored: {card.name}"
            else:
                # Need to add it since it's fleeting while not filled
                new_stable = Stable(stored=None)
                game.pile[player].append(new_stable)

                return super().play(player, game, index, bonus)
stable = Stable()
class Uprising(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.Crowd
        return super().play(player, game, index, bonus + index)
uprising = Uprising(name="Uprising", cost=6, points=3, text="6:3, worth 1 more for each card before this in the story")
class Juggle(Card):
    def on_play(self, player, game):
        amt = min(3, len(game.hand[player]))

        self.bottom(amt, game, player)
        self.draw(amt, game, player)
juggle = Juggle(name="Juggle", cost=1, points=1,
                text="1:1. When played, put up to 3 cards from your hand on the bottom of your deck, then draw that many")
class Paranoia(Card):
    def on_play(self, player, game):
        amt = game.story.get_length()
        game.vision[player] += amt

    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus)
paranoia = Paranoia(name="Paranoia", cost=3, points=3,
                    text="3:3, sight N (This round the first 4 cards of story are visible to you) (N is the number of cards before this in the story)")
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
horus = Horus(name="Horus", cost=7, points=7,
              text="7:7, costs 0 if you can see at least 3 of your opponent's cards in the story")
class Bandit(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(wanted_poster, game, player ^ 1)
bandit = Bandit(name="Bandit", cost=1, points=2, text="1:2, create a ${146} in your opponent's hand")
class Boar(Card):
    def play(self, player, game, index, bonus):
        amt = game.story.get_length()
        return super().play(player, game, index, bonus) + self.discard(amt, game, player)
boar = Boar(name="Boar", cost=3, points=4, text="3:4, discard your X leftmost cards, where X is the number of cards later in the story.")
class Disintegrate(Card):
    def play(self, player, game, index, bonus):
        result = super().play(player, game, index, bonus)

        replaced_card = None
        owner = None
        index = 0
        for act in game.story.acts:
            if act.card.cost == 1:
                replaced_card = act.card
                owner = act.owner
                break

            index += 1

        if replaced_card is not None:
            # The full act with which to replace player's final act
            replacement_act = Act(card=broken_bone,
                                  owner=owner,
                                  source=Source.PILE)

            game.story.replace_act(index, replacement_act)

            result += f'\n{broken_bone.name} replaced {replaced_card.name}'

        return result
disintegrate = Disintegrate(name="Disintegrate", cost=1, points=1,
              text="1:1, transform the next 1-cost card in the story into a Broken Bone.")
class Ecology(Card):
    def on_play(self, player, game):
        game.mana[player] += 10

    # def play(self, player, game, index, bonus):
    #     recap = super().play(player, game, index, bonus)
    #
    #     recap += self.tutor(index, game, player)
    #
    #     if len(game.hand[player]) > 0:
    #         rightmost_card = game.hand[player][-1]
    #
    #         game.deck[player].append(rightmost_card)
    #         recap += f"\nTop: {rightmost_card.name}"
    #
    #     return recap
ecology = Ecology(name="Ecology", cost=7, points=0,
                  text="7:2.\nWhen played, gain 10 mana this round.")
                  # text="8:6, Tutor X, where X is the number of cards before this in the story. Then create a copy of the rightmost card in your hand and put it on top of your deck.")
class Chimney(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if game.hand[player^1]:
            card = game.hand[player^1].pop(0)
            game.deck[player^1].append(card)

            game.animations[player^1].append(('Hand', 'Deck', CardCodec.encode_card(card)))

            recap += f'\nTop'

        return recap
chimney = Chimney(name="Chimney", cost=5, points=2, text="5:2, your opponent puts the leftmost card in their hand on top of their deck.")



"""Lists"""
hidden_card = Card(name="Cardback", cost=0, points=0, text="?")
full_catalog = [
    stars, bone_knife, cog, crossed_bones, dove, drown, dash, swift,
    gears, cosmos, factory, fruiting, gift, hurricane, dinosaur_bones, mine,
    chimney, tumulus, uprising, stalker, sarcophagus, anubis, ai, oak,

    bee, nectar, bandit, spy, night_vision, disintegrate, juggle, sine,
    fishing_boat, raise_dead, bastet, imprison, crypt, stable, boar, paranoia,
    pelican, beekeep, lotus, eagle, ecology, horus, icarus, enrage
    ]

non_collectibles = [hidden_card] + tokens
all_cards = full_catalog + non_collectibles

# Set the id of each card, temporary solution TODO When making new cards set the ids
i = 0
for card in all_cards:
    card.id = i
    i += 1

import random
# Get a random deck for the computer opponent
def get_computer_deck():
    # New deck using web-app cards:
    possible_decks = [
        [
            crossed_bones, crossed_bones, crossed_bones, crossed_bones, crossed_bones,
            swift, swift, swift,
            gift, gift, gift,
            dinosaur_bones, dinosaur_bones,
            tumulus, tumulus
        ], [
            stars,
            crossed_bones, crossed_bones, crossed_bones, crossed_bones,
            swift, swift, swift,
            gift, gift,
            dinosaur_bones, dinosaur_bones, mine, mine,
            oak
        ], [
            stars,
            crossed_bones, crossed_bones, crossed_bones, drown, drown, drown,
            swift, swift, fishing_boat,
            gift, gift,
            dinosaur_bones,
            sarcophagus,
            oak
        ]
    ]

    return random.choice(possible_decks)
