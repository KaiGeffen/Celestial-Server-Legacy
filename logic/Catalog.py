from logic.Card import *
from logic.Effects import Status, Quality
from logic.Story import Source, Act
from Animation import Animation

# TODO make a separate file for tokens
"""Tokens"""
class Seen(Card):
    def on_upkeep(self, player, game, index):
        game.vision[player ^ 1] += 4
        return True
seen = Seen(name="Seen", cost=2, qualities=[Quality.FLEETING], id=1001)
class Ashes(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.draw(1, game, player)
ashes = Ashes(name="Ashes", cost=1, qualities=[Quality.FLEETING], id=1002)
child = Card(name='Child', qualities=[Quality.FLEETING], id=1003)
class Predator(Card):
    def play(self, player, game, index, bonus):
        bonus += 2 * game.pile[player ^ 1].count(bandit)

        super().play(player, game, index, bonus)
predator = Predator(name="Predator", cost=1, qualities=[Quality.FLEETING], id=1004)

tokens = [seen, ashes, child, predator]

"""FIRE"""
dash = FireCard(name="Dash", cost=2, points=3, id=6)

"""BIRD"""
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

"""Discard"""
class BoneKnife(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        super().play(player, game, index, bonus)
        self.discard(1, game, opp)

        # game.sound_effect = SoundEffect.Cut

    def rate_play(self, world):
        return self.rate_discard(world)
bone_knife = BoneKnife(name="Bone Knife", cost=1, id=1)
class Stalker(Card):
    def get_cost(self, player, game):
        opp = (player + 1) % 2

        return len(game.hand[opp])

    def rate_delay(self, world):
        return 10
stalker = Stalker(name="Stalker", cost=6, points=3, id=19)
class Imprison(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        super().play(player, game, index, bonus)
        self.reset(game)

        game.score[opp] = len(game.hand[opp])

    def rate_play(self, world):
        # TODO Use a function for predicting opponent's hand size
        return self.rate_reset(world) - len(world.opp_hand)
imprison = Imprison(name="Imprison", cost=1, id=35)
class Gift(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for player in (0, 1):
            self.draw(1, game, player)

    def rate_play(self, world):
        return 3 + len(world.opp_hand)/2 - len(world.hand)/2
gift = Gift(name="Gift", cost=3, points=3, id=12)
class Symbiosis(Card):
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
symbiosis = Symbiosis(name="Symbiosis", cost=6, points=6, id=57)

class Nightmare(Card):
    def morning(self, player, game, index):
        if len(game.hand[player^1]) < len(game.hand[player]):
            super().create(stalker, game, player)
            return True
nightmare = Nightmare(name="Nightmare", cost=2, points=2, id=68)


"""Machines"""
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
class Sine(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.starve(4, game, player)

    def rate_delay(self, world):
        return 12
sine = Sine(name="Sine", cost=2, points=4, id=31)

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

"""Nature"""
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
class Fruiting(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.nourish(3, game, player)
fruiting = Fruiting(name="Fruiting", cost=3, id=11)
class Oak(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.gentle(game, player)
oak = Oak(name="Oak", cost=8, points=8, id=23)
class Bounty(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for player in (0, 1):
            self.nourish(2, game, player)
bounty = Bounty(name="Bounty", cost=3, points=3, id=48)

"""Earth"""
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
class NightVision(SightCard):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.tutor(2, game, player)
night_vision = NightVision(amt=3, name="Night Vision", cost=1, points=0, id=28)

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

"""Ships"""
class FishingBoat(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        for i in range(3):
            self.tutor(1, game, player)
fishing_boat = FishingBoat(name="Fishing Boat", cost=2, points=1, id=32)

"""Death"""
class Scarab(SightCard):
    def morning(self, player, game, index):
        game.vision[player] += 1
        return True
scarab = Scarab(amt=4, name="Scarab", cost=0, points=0, id=50)
class Drown(Card):
    def play(self, player, game, index, bonus):
        # game.sound_effect = SoundEffect.Drown
        super().play(player, game, index, bonus)
        self.mill(3, game, player)
drown = Drown(name="Drown", cost=1, points=1, id=5)
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
class Crypt(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

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
crypt = Crypt(name="Crypt", cost=2, points=2, id=36)

"""INSECTS"""
class Nectar(SightCard):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.nourish(1, game, player)
nectar = Nectar(name="Nectar", amt=3, cost=1, id=25)

"""Other"""
class Hurricane(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.reset(game)

    def rate_play(self, world):
        return self.rate_reset(world)
hurricane = Hurricane(name="Hurricane", cost=3, id=13)
class Spy(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.create(seen, game, player ^ 1)
spy = Spy(name="Spy", cost=1, id=27)
class Uprising(Card):
    def play(self, player, game, index, bonus):
        # game.sound_effect = SoundEffect.Crowd
        super().play(player, game, index, bonus + index)

    def rate_play(self, world):
        return len(world.story.acts)
uprising = Uprising(name="Uprising", cost=6, points=3, id=18)
class Awakening(Card):
    def play(self, player, game, index, bonus):
        self.add_status(1, game, player, Status.AWAKENED)

        super().play(player, game, index, bonus)
awakening = Awakening(name="Awakening", cost=3, points=3, id=39)
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
horus = Horus(name="Horus", cost=7, points=7, id=45)
class Bandit(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.create(predator, game, player ^ 1)
bandit = Bandit(name="Bandit", cost=1, points=2, id=26)
class Ecology(Card):
    def on_play(self, player, game):
        game.mana[player] += 10
ecology = Ecology(name="Ecology", cost=7, points=0, id=44)
class Chimney(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        if game.hand[player^1]:
            card = game.hand[player^1].pop(0)
            game.deck[player^1].append(card)

            game.animations[player^1].append(
                Animation('Hand', 'Deck', card=CardCodec.encode_card(card)))

    def rate_play(self, world):
        return self.points + self.rate_discard(world)
chimney = Chimney(name="Chimney", cost=5, points=3, id=16)

class PocketWatch(Card):
    def get_cost(self, player, game):
        cost = max(0, self.cost - game.amt_passes[player])
        return cost

    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.draw(2, game, player)
pocket_watch = PocketWatch(name="Pocket Watch", cost=4, points=2, id=54)
class Sun(Card):
    def morning(self, player, game, index):
        super().add_mana(2, game, player)
        return True
sun = Sun(name="Sun", cost=8, points=8, id=56)
class Sickness(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)
        self.starve(4, game, player ^ 1)
        self.create(sickness, game, player ^ 1)
sickness = Sickness(name="Sickness", cost=3, points=-1, qualities=[Quality.FLEETING], id=58)
class Axolotl(Card):
    def morning(self, player, game, index):
        super().create(axolotl, game, player)
        return True
axolotl = Axolotl(name="Axolotl", cost=1, points=1, id=63)
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

class Conquer(Card):
    def get_cost(self, player, game):
        num_seen_cards = 0
        for i in range(len(game.story.acts)):
            act = game.story.acts[i]
            if act.owner == player:
                num_seen_cards += 1
            else:
                if i + 1 <= game.vision[player] or Quality.VISIBLE in act.card.qualities:
                    num_seen_cards += 1

        return max(0, self.cost - num_seen_cards)
conquer = Conquer(name="Conquer", cost=5, points=3, id=67)

class Carrion(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        # Nourish amount is the number of Fleeting cards in the top 3 of the discard pile
        amt = sum(Quality.FLEETING in card.qualities for card in game.pile[player][-3:])

        # Remove the top 3 cards of discard pile from the game
        self.dig(3, game, player)

        self.nourish(amt, game, player)
carrion = Carrion(name="Carrion", cost=2, points=1, id=74)

class GentleRain(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        amt = game.amt_drawn[player]

        self.nourish(amt, game, player)
gentle_rain = GentleRain(name="Gentle Rain", cost=4, points=2, id=71)

class Sunflower(Card):
    def play(self, player, game, index, bonus):
        points = self.points + bonus
        points += game.status[player].count(Status.NOURISH)
        points -= game.status[player].count(Status.STARVE)

        super().play(player, game, index, bonus)

        self.inspire(points, game, player)
sunflower = Sunflower(name="Sunflower", cost=2, points=1, id=69)

class Hollow(Card):
    def play(self, player, game, index, bonus):
        super().play(player, game, index, bonus)

        amt = max(0, game.score[player])

        game.score[player] = 0

        self.nourish(amt, game, player)
hollow = Hollow(name="Hollow", cost=0, points=0, id=76)

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
    stars, bone_knife, cog, crossed_bones, dove, drown, dash, swift,
    gears, cosmos, factory, fruiting, gift, hurricane, dinosaur_bones, mine,
    chimney, tumulus, uprising, stalker, sarcophagus, anubis, the_future, oak,

    nectar, bandit, spy, night_vision, sine,
    fishing_boat, unearth, bastet, imprison, awakening,
    pelican, ecology, horus, icarus,

    bounty, scarab, phoenix, generator, pocket_watch, become_machine, sun,
    symbiosis,
    sickness, anvil,
    paramountcy, axolotl, parch, heron,
    conquer, nightmare, carrion, gentle_rain, sunflower, hollow, moon,

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

    if i is not None:
        try:
            return possible_decks[i]
        except:
            print('Invalid ai deck: ' + i)

    return random.choice(possible_decks)
