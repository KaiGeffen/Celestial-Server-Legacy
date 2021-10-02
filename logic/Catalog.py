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
        return True
camera = Camera(name="Camera", cost=2, qualities=[Quality.FLEETING],
                text="2:0, Fleeting, at the start of each round, give your opponent vision 4", id=1001)
class BrokenBone(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.BoneSnap
        return super().play(player, game, index, bonus)# + self.draw(1, game, player)
broken_bone = BrokenBone(name="Broken Bone", cost=1, qualities=[Quality.FLEETING], id=1002)
robot = Card(name='Robot', qualities=[Quality.FLEETING], text="0:X, Fleeting", id=1003)
class WantedPoster(Card):
    def play(self, player, game, index, bonus):
        bonus += 2 * game.pile[player ^ 1].count(bandit)

        return super().play(player, game, index, bonus)
wanted_poster = WantedPoster(name="Wanted Poster", cost=1, qualities=[Quality.FLEETING],
                             text="1:0, fleeting, +2 for each Bandit in your opponent's discard pile", id=1004)

tokens = [camera, broken_bone, robot, wanted_poster]

"""FIRE"""
dash = FireCard(name="Dash", cost=2, points=3, text="2:3, flare (Worth 1 less for every card before it)", id=6)
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
                text="8:2, give each card later in the story -X, where X is its cost.\nWhen played, give each card ealier in the story -X.", id=47)
class Desert(Card):
    def play(self, player, game, index, bonus):


        if game.story.acts:
            # The index of the card popped from the story
            story_index = index + len(game.story.acts)
            act = game.story.acts.pop()

            super().create(act.card, game, act.owner)
            game.animations[act.owner].pop()
            game.sound_effect = None

            hand_index = len(game.hand[act.owner]) - 1
            game.animations[act.owner].append(('Story', 'Hand', hand_index, story_index))
        else:
            bonus += 3

        recap = super().play(player, game, index, bonus)

        return recap
desert = Desert(name="Desert", cost=2, points=0, text="2:0, return the last in the story to its owner's hand", id=49)

"""BIRD"""
class Dove(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.Bird
        return super().play(player, game, index, bonus)
dove = Dove(name="Dove", cost=1, points=1, qualities=[Quality.VISIBLE, Quality.FLEETING],
            text="1:1, visible, fleeting (After resolving, this card is removed from the game instead of moving to your discard pile)",
            id=4)
class Swift(Card):
    def play(self, player, game, index, bonus):
        if not game.story.is_empty():
            if game.story.acts[0].card.cost == 1:
                bonus += 1

        return super().play(player, game, index, bonus)
swift = Swift(name="Swift", cost=2, points=2, qualities=[Quality.VISIBLE],
              text="2:2, visible, if the next card costs 1, +1", id=7)
class Pelican(Card):
    def play(self, player, game, index, bonus):
        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        recap = super().play(player, game, index, bonus + amt)
        recap += self.oust(amt, game, player)

        return recap
pelican = Pelican(name="Pelican", cost=4, points=4, text="4:4, oust each 0 or 1 cost card from your hand, +1 for each", id=40)
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
icarus = Icarus(name="Icarus", cost=7, points=7, text="7:7, costs 0 if you have 5 cards in story", id=46)
class Eagle(SightCard):
    def on_play(self, player, game):
        game.hand[player] = [dove] * len(game.hand[player])

        super().on_play(player, game)

    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(2, game, player)
eagle = Eagle(amt=4, name="Eagle", cost=6, points=6,
                    text="6:6, nourish 2. When played, gain sight 4 and transform each card in your hand into a Dove.", id=43)
class Vulture(Card):
    def pile_upkeep(self, player, game, index):
        # Only do it if this is the top card of the discard pile
        if index == len(game.pile[player]) - 1:
            super().create(dove, game, player)
            return True
vulture = Vulture(name="Vulture", cost=3, points=3, id=52)
class Phoenix(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(dove, game, player)
phoenix = Phoenix(name="Phoenix", cost=5, points=5, qualities=[Quality.FLEETING], id=51)

class Heron(Card):
    def play(self, player, game, index, bonus):
        amt_fleeting = 0
        for card in game.hand[player]:
            if Quality.FLEETING in card.qualities:
                amt_fleeting += 1

        super().play(player, game, index, bonus)

        self.inspire(amt_fleeting, game, player)
heron = Heron(name="Heron", cost=5, points=4, qualities=[Quality.FLEETING], id=65)

"""Discard"""
class BoneKnife(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(1, game, opp)
bone_knife = BoneKnife(name="Bone Knife", text="0:0, opponent discards 1", id=1)
class Stalker(Card):
    def get_cost(self, player, game):
        opp = (player + 1) % 2

        return len(game.hand[opp])
stalker = Stalker(name="Stalker", cost=6, points=4, id=19)
class Imprison(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        recap = super().play(player, game, index, bonus)
        recap += self.reset(game)

        game.score[opp] = len(game.hand[opp])
        recap += f'\n+{len(game.hand[opp])} opp'

        return recap
imprison = Imprison(name="Imprison", cost=2, text="2:0, reset, then give opponent 1 point for each card in their hand", id=35)
class Gift(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for player in (0, 1):
            recap += self.draw(1, game, player)

        return recap
gift = Gift(name="Gift", cost=3, points=3, text="3:3, both players draw 1", id=12)
class Symbiosis(Card):
    def play(self, player, game, index, bonus):
        nourished = Status.NOURISH in game.status[player]
        recap = super().play(player, game, index, bonus)
        if nourished:
            recap += super().discard(1, game, player^1)
        return recap
symbiosis = Symbiosis(name="Symbiosis", cost=6, points=6, id=57)

"""Machines"""
class Cog(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(1, game, player)
cog = Cog(name="Cog", cost=0, text="0:0, build 1 (+1 to a robot in your hand, or make a 0:1 fleeting robot)", id=2)
class Gears(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(2, game, player)
gears = Gears(name="Gears", cost=2, text="2:0, build 2", id=8)
class Factory(Card):
    def play(self, player, game, index, bonus):
        amt = game.story.get_length()
        return super().play(player, game, index, bonus) + self.build(amt, game, player)
factory = Factory(name="Factory", cost=3, text="3:0, build X, where X is number of cards later in the story", id=10)
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
ai = AI(name="AI", cost=8, points=5, text="8:5, draw 1. Costs X less where X is total robot points in hand", id=22)
class Sine(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.starve(4, game, player)
sine = Sine(name="Sine", cost=2, points=4, text="2:4, starve 4 (Your next card gives -4 points)", id=31)

class Generator(Card):
    def pile_upkeep(self, player, game, index):
        # Only do it if this is the top card of the discard pile
        if index == len(game.pile[player]) - 1:
            super().build(1, game, player)
            return True
generator = Generator(name="Generator", cost=4, points=4, id=53)
class BecomeMachine(Card):
    def play(self, player, game, index, bonus):
        result = super().play(player, game, index, bonus)

        index = 0
        for act in game.story.acts:
            if act.owner == player:
                amt = act.card.cost
                card = Card(name='Robot', points=amt, qualities=[Quality.FLEETING], dynamic_text=f'0:{amt}, Fleeting',
                            id=1003)
                self.transform(index, card, game)

            index += 1
become_machine = BecomeMachine(name="Become Machine", cost=1, points=1, qualities=[Quality.FLEETING], id=55)
class Cogsplosion(Card):
    def play(self, player, game, index, bonus):
        index = -1
        for card in game.hand[player]:
            index += 1

            if card.name == 'Robot':
                bonus += card.points

                return super().play(player, game, index, bonus) + self.discard(1, game, player, index=index)

        return ''
cogsplosion = Cogsplosion(name="Cogsplosion", cost=4, id=59)
class Anvil(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(2, game, player)
anvil = Anvil(name="Anvil", cost=3, points=2, id=60)

"""Nature"""
class Stars(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.inspire(1, game, player)
stars = Stars(name="Stars", text="0:0, inspire (Next turn gain 1 temporary mana)", id=0)
class Cosmos(Card):
    def play(self, player, game, index, bonus):
        amt = 1
        for act in game.story.acts:
            if act.owner == player:
                amt += 1
        return super().play(player, game, index, bonus) + self.inspire(amt, game, player)
cosmos = Cosmos(name="Cosmos", cost=2, text="2:0, inspire 1 + 1 for each card you play later this round", id=9)
class Fruiting(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(3, game, player)
fruiting = Fruiting(name="Fruiting", cost=3, text="3:0, nourish 3 (Your next card gives +3 points)", id=11)
class Lotus(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.inspire(2, game, player)

        if self.your_final(game, player):
            recap += self.reset(game)

        return recap
lotus = Lotus(name="Lotus", cost=5, text="5:0, inspire 2, final: reset", id=42)
class Oak(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.gentle(game, player)
oak = Oak(name="Oak", cost=8, points=8,
          text="8:8, gentle (If you win this round, convert to nourish any points not needed to win)", id=23)
class Bounty(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for player in (0, 1):
            recap += self.nourish(2, game, player)

        return recap
bounty = Bounty(name="Bounty", cost=3, points=3, text="3:3, both players Nourish 2", id=48)

class Cornucopia(Card):
    def get_cost(self, player, game):

        seen_costs = []
        for i in range(len(game.story.acts)):
            act = game.story.acts[i]

            # Skip cards that you can't see
            if act.owner == player:
                pass
            # Can see it because have vision
            elif i + 1 <= game.vision[player]:
                pass
            # Can see it because it's visible
            elif Quality.VISIBLE in act.card.qualities:
                pass
            else:
                continue

            cost = act.card.cost
            if cost not in seen_costs:
                seen_costs.append(cost)

        return max(0, self.cost - len(seen_costs))
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(5, game, player)
cornucopia = Cornucopia(name="Cornucopia", cost=6, points=0, id=61)
"""Earth"""
class CrossedBones(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += '\nBury:'
        for _ in range(2):
            recap += self.create_in_pile(broken_bone, game, player)

        return recap
crossed_bones = CrossedBones(name="Crossed Bones", cost=1, points=2, qualities=[Quality.FLEETING], id=3)
class Mine(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.dig(4, game, player)

        return recap
mine = Mine(name="Mine", cost=4, points=4, text="4:4, oust the top 4 cards of your discard pile", id=15)
class DinosaurBones(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += '\nBury:'
        for _ in range(3):
            recap += self.create_in_pile(broken_bone, game, player)

        return recap
dinosaur_bones = DinosaurBones(name="Dinosaur Bones", cost=4, points=5, qualities=[Quality.FLEETING], id=14)
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

        recap = super().play(player, game, index, bonus)

        game.sound_effect = SoundEffect.Meow
        return recap
bastet = Bastet(1)
class NightVision(SightCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(2, game, player)

        return recap
night_vision = NightVision(amt=3, name="Night Vision", cost=1, points=0, text="1:0, tutor 2. On play, sight 3", id=28)

class FishBones(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += '\nBury:'
        for _ in range(3):
            recap += self.create_in_pile(broken_bone, game, player)

        recap += self.draw(2, game, player)

        return recap
fish_bones = FishBones(name="Fish Bones", cost=2, points=0, qualities=[Quality.FLEETING], id=64)

"""Ships"""
class FishingBoat(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for i in range(3):
            recap += self.tutor(1, game, player)

        return recap
fishing_boat = FishingBoat(name="Fishing Boat", cost=2, text="2:0, tutor a 1 3 times", id=32)

"""Death"""
class Scarab(SightCard):
    def pile_upkeep(self, player, game, index):
        # Only do it if this is the top card of the discard pile
        if index == len(game.pile[player]) - 1:
            game.vision[player] += 1
            return True
scarab = Scarab(amt=4, name="Scarab", cost=0, points=0, id=50)
class Drown(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.Drown
        return super().play(player, game, index, bonus) + self.mill(3, game, player)
drown = Drown(name="Drown", cost=1, points=1, text="1:1, mill yourself 3 (Top 3 cards of deck go to pile)", id=5)
class RaiseDead(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if game.pile[player]:
            card = game.pile[player].pop()
            game.deck[player].append(card)

            recap += f'\nRaise {card.name}'
            game.animations[player].append(('Discard', 'Deck', CardCodec.encode_card(card)))

        return recap
raise_dead = RaiseDead(name="Raise Dead", cost=2, points=2, text="2:2 put the top card of your pile on top of deck", id=33)
class Tumulus(Card):
    def play(self, player, game, index, bonus):
        if len(game.pile[player]) >= 8:
            bonus += 2

        return super().play(player, game, index, bonus)
tumulus = Tumulus(name="Tumulus", cost=5, points=4, id=17)
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
                          text="6:X, put the highest cost card from your pile on top of your deck, X is its cost", id=20)
class Anubis(Card):
    def get_cost(self, player, game):
        if len(game.pile[player]) >= 12:
            return 0
        else:
            return self.cost
anubis = Anubis(name="Anubis", cost=7, points=7, id=21)
class Crypt(Card):
    def play(self, player, game, index, bonus):
        result = super().play(player, game, index, bonus)

        index_final_owned_card = -1
        final_card = None
        index = 0
        for act in game.story.acts:
            if act.owner == player:
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
                self.transform(index_final_owned_card, replacement_card, game)
crypt = Crypt(name="Crypt", cost=2, points=2,
              text="2:2, your last unsprung card this round transforms into the first card in your pile with the same cost as it", id=36)

"""INSECTS"""
bee = Card(name="Bee", cost=0, points=1, qualities=[Quality.VISIBLE], text="0:1, visible", id=24)
class Nectar(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(1, game, player)
nectar = Nectar(name="Nectar", cost=1, text="1:0, nourish 1 (Your next card gives +1 points)", id=25)
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

        super().__init__(name=name, cost=cost, points=points, qualities=qualities, text=text, dynamic_text=dynamic_text, id=41)

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
hurricane = Hurricane(name="Hurricane", cost=4, text="4:0, reset", id=13)
class Spy(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(camera, game, player ^ 1)
spy = Spy(name="Spy", cost=1, text="1:0, create a 2:0 camera in opponent's hand which gives you sight each upkeep", id=27)
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

        super().__init__(name=name, cost=cost, points=points, qualities=qualities, text=text, dynamic_text=dynamic_text, id=37)

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
uprising = Uprising(name="Uprising", cost=6, points=3, text="6:3, worth 1 more for each card before this in the story", id=18)
class Juggle(Card):
    def on_play(self, player, game):
        amt = min(3, len(game.hand[player]))

        self.bottom(amt, game, player)
        self.draw(amt, game, player)
juggle = Juggle(name="Juggle", cost=1, points=1,
                text="1:1. When played, put up to 3 cards from your hand on the bottom of your deck, then draw that many", id=30)
class Paranoia(Card):
    def on_play(self, player, game):
        amt = game.story.get_length()
        game.vision[player] += amt

    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus)
paranoia = Paranoia(name="Paranoia", cost=3, points=3,
                    text="3:3, sight N (This round the first 4 cards of story are visible to you) (N is the number of cards before this in the story)", id=39)
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
              text="7:7, costs 0 if you can see at least 3 of your opponent's cards in the story", id=45)
class Bandit(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(wanted_poster, game, player ^ 1)
bandit = Bandit(name="Bandit", cost=1, points=2, text="1:2, create a ${146} in your opponent's hand", id=26)
class Boar(Card):
    def play(self, player, game, index, bonus):
        amt = game.story.get_length()
        return super().play(player, game, index, bonus) + self.discard(amt, game, player)
boar = Boar(name="Boar", cost=3, points=4, text="3:4, discard your X leftmost cards, where X is the number of cards later in the story.", id=38)
class Disintegrate(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        target_index = 0
        for act in game.story.acts:
            if act.card.cost == 1:
                self.transform(target_index, broken_bone, game)
                return
            target_index += 1
disintegrate = Disintegrate(name="Disintegrate", cost=1, points=1,
              text="1:1, transform the next 1-cost card in the story into a Broken Bone.", id=29)
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
                  text="7:2.\nWhen played, gain 10 mana this round.", id=44)
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
chimney = Chimney(name="Chimney", cost=5, points=2, text="5:2, your opponent puts the leftmost card in their hand on top of their deck.", id=16)

class PocketWatch(Card):
    def get_cost(self, player, game):
        cost = max(0, self.cost - game.amt_passes[player])
        return cost

    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.draw(2, game, player)
        return recap
pocket_watch = PocketWatch(name="Pocket Watch", cost=4, points=1, id=54)
class Sun(Card):
    def pile_upkeep(self, player, game, index):
        # Only do it if this is the top card of the discard pile
        if index == len(game.pile[player]) - 1:
            super().add_mana(2, game, player)
            return True
sun = Sun(name="Sun", cost=8, points=8, id=56)
class Sickness(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.starve(4, game, player ^ 1)
        recap += self.create(sickness, game, player ^ 1)
        return recap
sickness = Sickness(name="Sickness", cost=3, points=0, qualities=[Quality.FLEETING], id=58)
class Axolotl(Card):
    def pile_upkeep(self, player, game, index):
        # Only do it if this is the top card of the discard pile
        if index == len(game.pile[player]) - 1:
            super().create(axolotl, game, player)
            return True
axolotl = Axolotl(name="Axolotl", cost=1, points=1, id=63)

class Paramountcy(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        # Up to the number of spaces left, pop from discard pile and add to story
        space = 12 - (index + 1 + len(game.story.acts))
        for i in range(min(space, 5)):
            if game.pile[player]:
                card = game.pile[player].pop()
                game.story.add_act(card, player, Source.PILE)

                story_index = len(game.story.acts) - 1
                game.animations[player].append(('Discard', 'Story', story_index))


paramountcy = Paramountcy(name="Paramountcy", cost=9, points=0, id=62)


"""Lists"""
hidden_card = Card(name="Cardback", cost=0, points=0, text="?", id=1000)
full_catalog = [
    stars, bone_knife, cog, crossed_bones, dove, drown, dash, swift,
    gears, cosmos, factory, fruiting, gift, hurricane, dinosaur_bones, mine,
    chimney, tumulus, uprising, stalker, sarcophagus, anubis, ai, oak,

    bee, nectar, bandit, spy, night_vision, disintegrate, juggle, sine,
    fishing_boat, raise_dead, bastet, imprison, crypt, stable, boar, paranoia,
    pelican, beekeep, lotus, eagle, ecology, horus, icarus, enrage,

    bounty, desert, scarab, phoenix, vulture, generator, pocket_watch, become_machine, sun,
    symbiosis,
    sickness, cogsplosion, anvil,
    paramountcy, axolotl, cornucopia, fish_bones, heron
    ]

non_collectibles = [hidden_card] + tokens
all_cards = full_catalog + non_collectibles

import random
# Get a random deck for the computer opponent
def get_computer_deck():
    # Not too strong, aiming for C tier core set decks
    # 2 each of anubis, aggro, uprising, oak, stalker

    # New deck using web-app cards:
    possible_decks = [
        [
            # Standard anubis
            crossed_bones, crossed_bones, crossed_bones, drown, drown,
            swift, swift, dash,
            gift, fruiting,
            dinosaur_bones, dinosaur_bones,
            tumulus, tumulus,
            anubis,
        ], [
            # All in anubis
            stars, stars,
            crossed_bones, crossed_bones, drown, drown, drown,
            dinosaur_bones, dinosaur_bones, dinosaur_bones, dinosaur_bones,
            tumulus,
            sarcophagus,
            anubis, anubis,
        ], [
            # Aggro Anubis
            stars,
            crossed_bones, crossed_bones, crossed_bones, crossed_bones, crossed_bones,
            dash, dash, swift, swift,
            gift, gift,
            mine, mine,
            anubis
        ], [
            # Standard oak
            stars, stars, stars,
            dove, dove, dove,
            cosmos, swift,
            gift, gift, fruiting, fruiting,
            dinosaur_bones,
            anubis,
            oak,
        ], [
            # Sarco oak
            stars, stars, stars,
            dove, drown, drown,
            cosmos, gears,
            gift, fruiting,
            stalker, uprising, sarcophagus, sarcophagus,
            oak,
        ], [
            # Uprising
            cog, cog,
            dove, dove, crossed_bones,
            gears, gears, gears, swift, dash,
            gift, gift, gift,
            uprising, uprising,
        ], [
            # Uprising + Factory
            cog, cog, cog,
            dove, dove, dove, crossed_bones,
            cosmos, swift, dash,
            factory, gift, gift,
            uprising, stalker,
        ], [
            # Aggro
            stars,
            dove, crossed_bones, crossed_bones, crossed_bones, crossed_bones,
            gears, swift, swift, dash, dash,
            gift, gift, gift,
            mine,
        ], [
            # Bad stalker
            stars, stars,
            dove, dove, dove,
            swift, swift,
            fruiting, fruiting,
            chimney, chimney, chimney,
            stalker, stalker, sarcophagus,
        ], [
            # Stalker oak
            stars, stars, stars,
            dove, dove, dove,
            cosmos,
            fruiting, fruiting,
            chimney, chimney, chimney,
            stalker, stalker, sarcophagus,
            oak
        ], [
            # Aggro to late hyperthin
            dove, dove, dove, dove, dove, dove,
            dash, dash,
            gift, gift, gift,
            dinosaur_bones, dinosaur_bones,
            oak, oak,
        ]
    ]

    return random.choice(possible_decks)
