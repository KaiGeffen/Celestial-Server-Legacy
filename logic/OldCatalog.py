from logic.Card import *
from logic.Effects import Status, Quality

hidden_card = Card(name="Cardback", cost=0, points=0, text="?")

# Vanilla cards
rat = Card(name="Rat", cost=1, points=1, text="1:1")
cat = Card(name="Cat", cost=2, points=2, text="2:2")
swan = Card(name="Swan", cost=3, points=3, text="3:3")
cow = Card(name="Cow", cost=4, points=4, text="4:4")
gorilla = Card(name="Gorilla", cost=5, points=5, text="5:5")
elephant = Card(name="Elephant", cost=6, points=6, text="6:6")
dino = Card(name="Dino", cost=7, points=8, text="7:8")

# Carryover
class Stars(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.inspire(1, game, player)
stars = Stars(name="Stars", text="Inspire (Next turn gain 1 temporary mana)")
class Cosmos(Card):
    def play(self, player, game, index, bonus):
        amt = 1
        for (card, owner) in game.stack:
            if owner == player:
                amt += 1
        return super().play(player, game, index, bonus) + self.inspire(amt, game, player)
cosmos = Cosmos(name="Cosmos", cost=2, text="2: Inspire 1 + 1 for each card you play later this round")


# Control
class Hurricane(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.reset(game)
hurricane = Hurricane(name="Hurricane", cost=4, text="4: Reset")



"""FIRE"""
class Ember(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.discard(1, game, player)
        return  recap
ember = Ember(name="Ember", cost=1, points=2, text="1:2, discard 1")
dash = FireCard(name="Dash", cost=2, points=3, text="2:3, flare (Worth 1 less for every card before it)")
class Firewall(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.counter(game)

        return recap
firewall = Firewall(name="Firewall", cost=2, text="2: counter the next card")
class Charcoal(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.oust(1, game, player)
        return  recap
charcoal = Charcoal(name="Charcoal", cost=3, points=4, text="3:4, oust 1")
class Kindle(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for player in (0, 1):
            recap += self.discard(1, game, player)

        return recap
kindle = Kindle(name="Kindle", cost=3, points=3, text="3:3, both players discard 1")
force = FireCard(name="Force", cost=5, points=6, text="5:6, flare")
class BurningSkull(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        # Each player discards down to the lower of both player's hands
        min_hand = min(len(game.hand[0]), len(game.hand[1]))
        for player in {0, 1}:
            amt = len(game.hand[player]) - min_hand
            for i in range(amt):
                recap += self.discard(1, game, player)

        return  recap
burning_skull = BurningSkull(name="Burning Skull", cost=6, points=4,
                             text="6:4, both players discard to lower hand size")
class Volcano(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.counter(game)

        return recap
volcano = Volcano(name="Volcano", cost=8, points=5, text="8:5, counter the next card")



""""BIRDS"""
class Stork(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(1, game, player)
        return  recap
stork = Stork(name="Stork", text="0: Tutor a 1 cost card")
dove = Card(name="Dove", cost=1, points=1, qualities=[Quality.VISIBLE, Quality.FLEETING], text="1:1, fleeting")
class Owl(SightCard):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.flock(1, game, player)
owl = Owl(name="Owl", cost=1, text="1: flock, this round stack is visible to you")
class Twitter(Card):
    def play(self, player, game, index, bonus):
        amt = 0
        for (card, owner) in game.stack:
            if card is dove:
                amt += 1

        return super().play(player, game, index, bonus + amt)
twitter = Twitter(name="Twitter", cost=1, qualities=[Quality.VISIBLE], text="1:X, visible, where x is later doves on stack")
nest = FlockCard(name="Nest", amt=3, cost=2, points=1, text="2:1, flock 3")
phoenix = FlockCard(name="Phoenix", amt=1, cost=5, points=5, qualities=[Quality.VISIBLE], text="5:5, visible, flock 1")
class Vulture(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.oust(1, game, player)
        recap += self.flock(2, game, player)
        return  recap
vulture = Vulture(name="Vulture", cost=3, points=3, text="3:3, oust 1 flock 2")
class Peace(Card):
    def play(self, player, game, index, bonus):
        for (card, owner) in game.stack:
            if card is dove:
                return super().play(player, game, index, bonus) + self.reset(game)

        return super().play(player, game, index, bonus)
peace = Peace(name="Peace", cost=3, qualities=[Quality.VISIBLE], text="3: reset if a dove is later on the stack")
class Pelican(Card):
    def play(self, player, game, index, bonus):
        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        recap = super().play(player, game, index, bonus + amt)
        recap += self.oust(amt, game, player)

        return recap
pelican = Pelican(name="Pelican", cost=4, points=4, text="4:4, oust 0/1s in hand, +1 for each")
class Ostrich(Card):
    def get_cost(self, player, game):
        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        return 8 - amt
ostrich = Ostrich(name="Ostrich", cost=8, points=6, text="8:6, costs 1 less for each 0/1 in hand")


"""NATURE"""
class Shoot(Card):
    def play(self, player, game, index, bonus):
        if game.score[player] == 0:
            bonus += 1

        return  super().play(player, game, index, bonus)
shoot = Shoot(name="Shoot", text="0:0, +1 if you have 0 points")
class Stump(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.create(pine, game, player)
        return  recap
stump = Stump(name="Stump", text="0: Create a Pine in your hand")
class Roots(Card):
    def play(self, player, game, index, bonus):
        your_last_card_cost = self.cost
        for (card, owner) in game.stack:
            if owner == player:
                your_last_card_cost = card.cost

        if your_last_card_cost >= 4:
            bonus += 1

        recap = super().play(player, game, index, bonus)
        return  recap
roots = Roots(name="Roots", cost=1, points=1, text="1:1, +1 if your final card costs 4+")
class Sprout(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.inspire(1, game, player)
        recap += self.tutor(4, game, player)
        return  recap
sprout = Sprout(name="Sprout", cost=2, text="2: Inspire, tutor a 4")
class Fruiting(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(3, game, player)
fruiting = Fruiting(name="Fruiting", cost=3, text="3: Nourish 3 (Your next card gives +3 points)")
class Pine(Card):
    def play(self, player, game, index, bonus):
        if self.your_final(game, player):
            bonus += 2

        return super().play(player, game, index, bonus) + self.gentle(game, player)
pine = Pine(name="Pine", cost=4, points=2, text="4:2, Gentle, final: +2")
class Bulb(Card):
    def play(self, player, game, index, bonus):
        if game.status[player].count(Status.NOURISH) > 0:
            bonus += 2

        return super().play(player, game, index, bonus)
bulb = Bulb(name="Bulb", cost=4, points=3, text="4:3, +2 if nourished")
class Lotus(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.inspire(2, game, player)

        if self.your_final(game, player):
            recap += self.reset(game)

        return recap
lotus = Lotus(name="Lotus", cost=5, text="5: Inspire 2, final: reset")
class LeafSwirl(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if self.your_final(game, player):
            amt = len(game.hand[player])
            recap += self.oust(amt, game, player)
            recap += self.draw(amt, game, player)

        return recap
leaf_swirl = LeafSwirl(name="Leaf Swirl", cost=5, points=5, text="5:5 final: oust your hand, draw that many cards")
class Pollen(Card):
    def play(self, player, game, index, bonus):
        if self.your_final(game, player):
            bonus += 3

        recap = super().play(player, game, index, bonus)
        recap += self.tutor(0, game, player)

        return recap
pollen = Pollen(name="Pollen", cost=6, points=3, text="6:3, tutor a 0, final: +3")

class Oak(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.gentle(game, player)
oak = Oak(name="Oak", cost=8, points=8, text="8:8, gentle (If you win this round, convert to nourish any extra points)")



"""SNAKES"""
snake_egg_spring = Card(name="Snake Egg", points=1, qualities=[Quality.FLEETING], text="1:1, spring: 1 point")
snake_egg = Card(name="Snake Egg", cost=1, points=1, text="1:1, spring: 1 point", spring=snake_egg_spring)

class Ouroboros(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.oust(3, game, player)
        recap += self.draw(3, game, player)
        return  recap
ouroboros_spring = Ouroboros(name="Ouroboros", qualities=[Quality.FLEETING], text="2:2, spring: oust 3 draw 3")
ouroboros = Card(name="Ouroboros", cost=2, points=2, text="2 for 2, spring: oust 3 draw 3", spring=ouroboros_spring)

class Serpent(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(1, game, opp)
serpent_spring = Serpent(name="Serpent", qualities=[Quality.FLEETING], text="3:3, spring: opponent discards 1")
serpent = Card(name="Serpent", cost=3, points=3, text="3:3, spring: opponent discards 1", spring=serpent_spring)

salamander_spring = FireCard(name="Salamander", points=4, qualities=[Quality.FLEETING], text="4:4, flare, spring: 4 points")
salamander = FireCard(name="Salamander", cost=4, points=4, text="4:4, flare, spring: 4 points", spring=salamander_spring)

class Temptation(Card):
    def play(self, player, game, index, bonus):
        game.status = [[], []]
        return super().play(player, game, index, bonus) + '\nStatus Gone'
temptation_spring = Temptation(name="Temptation", qualities=[Quality.FLEETING],
                               text="4:4, spring: remove all status (Boost, inspire, gentle)")
temptation = Card(name="Temptation", cost=4, points=4,
                  text="4:4, spring: remove all status (Boost, inspire, gentle)", spring=temptation_spring)

class SandSnake(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.draw(1, game, player)

        return recap
sand_snake_spring = SandSnake(name="Sand Snake", qualities=[Quality.FLEETING], text="5:5, spring: draw 1")
sand_snake = Card(name="Sand Snake", cost=5, points=5, text="5:5, spring: draw 1", spring=sand_snake_spring)

class FrogPrince(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.inspire(2, game, player)
frog_prince_spring = FrogPrince(name="Frog Prince", qualities=[Quality.FLEETING], text="6:6, spring: inspire 2")
frog_prince = Card(name="Frog Prince", cost=6, points=6, text="6:6, spring: inspire 2", spring=frog_prince_spring)

class Wyvern(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.flock(3, game, player)
wyvern_spring = Wyvern(name="Wyvern", qualities=[Quality.FLEETING], text="7:7, spring: flock 3")
wyvern = Card(name="Wyvern", cost=7, points=7, text="7:7, spring: flock 3", spring=wyvern_spring)

class Cobra(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(2, game, player)
        return  recap
cobra_spring = Cobra(name="Cobra", qualities=[Quality.FLEETING], text="8:9, spring: tutor a 2")
cobra = Card(name="Cobra", cost=8, points=9, text="8:9, spring: tutor a 2", spring=cobra_spring)


"""Fish"""
class StarFish(FlowCard):
    def on_flow(self, player, game):
        game.mana[player] += 1
        return super().on_flow(player, game)
star_fish = StarFish(name="Star Fish", text="0: flow: Gain 1 mana")
flying_fish = FlowCard(name="Flying Fish", cost=1, points=1, text="1:1, flow (As soon as you ebb, cycle this)")
class Perch(FlowCard):
    def play(self, player, game, index, bonus):
        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        recap = super().play(player, game, index, bonus + amt)
        recap += self.oust(amt, game, player)

        return recap
perch = Perch(name="Perch", cost=2, points=2, text="2:2, flow, oust 0/1s in hand, +1 for each")
class Dolphin(FlowCard):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        if game.score[player] == game.score[opp] - 5:
            bonus += 4

        return super().play(player, game, index, bonus)
dolphin = Dolphin(name="Dolphin", cost=3, points=2, text="3:2, flow, +4 if opponent leads by 5 points")
class Angler(FlowCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(1, game, player)

        return recap
angler = Angler(name="Angler", cost=4, points=4, qualities=[Quality.VISIBLE], text="4:4, flow, visible, tutor 1")
class Piranha(FlowCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.counter(game)

        return recap
piranha = Piranha(name="Piranha", cost=4, points=1, text="4:1 flow, counter the next card")
class SchoolOfFish(FlowCard):
    def get_cost(self, player, game):
        amt = 0
        for (card, owner) in game.stack:
            if owner == player and card.cost == 1:
                amt += 1

        return self.cost - amt
school_of_fish = SchoolOfFish(name="School of Fish", cost=5, points=5, text="5:5, flow, costs 1 less for each 1-cost you have on stack")
class Whale(FlowCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for card in game.hand[player]:
            if card.cost == 1:
                recap += self.reset(game)
                break

        return recap
whale = Whale(name="Whale", cost=6, points=6, text="6:6, flow, if you have a 1 in hand, reset")
squid = FlowCard(name="Squid", cost=8, points=8, text="8:8, flow (As soon as you ebb, cycle this)")


"""Ships"""
class Raft(EbbCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        if len(game.hand[player]) == 0:
            recap += self.draw(1, game, player)

        return recap
raft = Raft(name="Raft", cost=1, points=1, text="1:1, ebb, if your hand is empty draw 1")
class Figurehead(EbbCard):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.inspire(2, game, player)
figurehead = Figurehead(name="Figurehead", cost=1, text="1: ebb, inspire 2")
class CrowsNest(EbbCard, SightCard):
    def on_play(self, player, game):
        EbbCard.on_play(self, player, game)
        SightCard.on_play(self, player, game)

    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.flock(1, game, player)
        return recap
crows_nest = CrowsNest(name="Crows Nest", cost=2, points=1, text="2:1, ebb, vision, flock 1")
class FishingBoat(EbbCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for i in range(3):
            recap += self.tutor(1, game, player)

        return recap
fishing_boat = FishingBoat(name="Fishing Boat", cost=3, text="3: ebb, tutor 1 x 3")
drakkar = EbbCard(name="Drakkar", cost=3, points=3, text="3:3, ebb")
class ShipWreck(EbbCard):
    def get_cost(self, player, game):
        opp = (player + 1) % 2
        amt = game.wins[opp] - game.wins[player]

        return self.cost - amt
ship_wreck = ShipWreck(name="Ship Wreck", cost=4, points=3,
                       text="4:3, ebb, costs 1 less for each round-win you are behind by (Cost more if you are ahead)")
trireme = EbbCard(name="Trireme", cost=5, points=5, text="5:5, ebb")



"""Discard"""
class BoneKnife(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(1, game, opp)
bone_knife = BoneKnife(name="Bone Knife", text="0: opponent discards 1")
class Maat(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        amt = 0
        for (card, owner) in game.stack:
            if owner == opp:
                amt += 1

        if amt == len(game.hand[opp]):
            bonus += 3

        return super().play(player, game, index, bonus)
maat = Maat(name="Maat", text="0:0, +3 if opponent has same number of cards in hand and stack")
class Robe(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        bonus -= len(game.hand[opp])

        return  super().play(player, game, index, bonus)
robe = Robe(name="Robe", cost=1, points=3, text="1:3, -1 for each card in opponent's hand")
class Cultist(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        recap = super().play(player, game, index, bonus)
        recap += self.discard(1, game, opp)
        recap += self.tutor(8, game, player)

        return  recap
cultist = Cultist(name="Cultist", cost=2, text="2: opponent discards 1, tutor an 8")
class Stalker(Card):
    def get_cost(self, player, game):
        opp = (player + 1) % 2

        return len(game.hand[opp])
stalker = Stalker(name="Stalker", cost=6, points=4, text="X:4, X is cards in opp's hand")
class Imprison(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        recap = super().play(player, game, index, bonus)
        recap += self.reset(game)

        game.score[opp] = len(game.hand[opp])
        recap += f'\n+{len(game.hand[opp])} opp'

        return recap
imprison = Imprison(name="Imprison", cost=2, text="2: Reset, then give opponent 1 point for each card in their hand")
class Gift(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for player in (0, 1):
            recap += self.draw(1, game, player)

        return recap
gift = Gift(name="Gift", cost=3, points=3, text="3:3, both players draw 1")
class Carnivore(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        if game.hand[opp]:
            if game.hand[opp][0].cost <= 1:
                bonus += 1

        return super().play(player, game, index, bonus) + self.discard(1, game, opp)
carnivore = Carnivore(name="Carnivore", cost=4, points=3, text="4:3, opponent discards 1, +1 if that card is a 0/1")
class Kenku(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        recap = super().play(player, game, index, bonus)
        recap += self.oust(amt, game, player)
        recap += self.discard(amt, game, opp)

        return recap
kenku = Kenku(name="Kenku", cost=6, points=5, text="6:5, oust all your 0/1 cost cards, opponent discards that many")
class Nightmare(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(2, game, opp)
nightmare = Nightmare(name="Nightmare", cost=8, points=5, text="8:5, opponent discards 2")



"""Machines"""
class Drone(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(0, game, player)
        return  recap
drone = Drone(name="Drone", cost=1, text="1: tutor 0")
class Cog(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(1, game, player)
cog = Cog(name="Cog", cost=0, text="0: build 1 (+1 to a robot in your hand, or make a 0:1 fleeting robot)")
class Gears(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(2, game, player)
gears = Gears(name="Gears", cost=2, text="2: build 2")
class Factory(Card):
    def play(self, player, game, index, bonus):
        amt = len(game.stack)
        return super().play(player, game, index, bonus) + self.build(amt, game, player)
factory = Factory(name="Factory", cost=3, text="3: build X, where X is number of later cards on stack")
class Anvil(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(2, game, player)
anvil = Anvil(name="Anvil", cost=4, points=3, text="4:3 build 2")
class Cogsplosion(Card):
    def play(self, player, game, index, bonus):
        index = -1
        for card in game.hand[player]:
            index += 1

            if card.name == 'Robot':
                bonus += card.points

                return super().play(player, game, index, bonus) + self.discard(1, game, player, index=index)

        return ''
cogsplosion = Cogsplosion(name="Cogsplosion", cost=4, text="4:X, Discard your first 0/X robot")
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
sine = Sine(name="Sine", cost=2, points=4, text="2:4 starve 4 (Your next card gives -4 points)")
class Foundry(Card):
    def play(self, player, game, index, bonus):
        amt = min(index, self.points)
        bonus -= amt

        recap = super().play(player, game, index, bonus)
        recap += self.build(amt, game, player)

        return recap
foundry = Foundry(name="Foundry", cost=5, points=5, text="5:5-X, build X, where X is cards on stack before this card")


"""Rock"""
# class FishBones(Card):
#     def play(self, player, game, index, bonus):
#         for _ in range(1):
#             game.pile[player].append(broken_bone)
#
#         return super().play(player, game, index, bonus)
# fish_bones = FishBones(name="Fish Bones", cost=0, points=1, qualities=[Quality.FLEETING],
#                              text="0:1, becomes 1x 1:0 fleeting bones after resolving")

class CrossedBones(Card):
    def play(self, player, game, index, bonus):
        for _ in range(2):
            game.pile[player].append(broken_bone)

        return super().play(player, game, index, bonus)
crossed_bones = CrossedBones(name="Crossed Bones", cost=1, points=2, qualities=[Quality.FLEETING],
                             text="1:2, becomes 2x 1:0 fleeting bones after resolving")
class Dig(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += '\nRemove:'
        for i in range(2):
            if game.pile[player]:
                card = game.pile[player].pop()
                recap += f'\n{card.name}'

        return recap
dig = Dig(name="Dig", cost=2, points=2, text="2:2, Oust the top 2 cards of your discard pile")
class Gnaw(Card):
    def play(self, player, game, index, bonus):
        for (card, owner) in game.stack:
            if card is broken_bone:
                bonus += 3

        return super().play(player, game, index, bonus)
gnaw = Gnaw(name="Gnaw", cost=3, points=3, text="3:3, +3 if there is a broken bone on stack")
class Mine(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += '\nRemove:'
        for i in range(4):
            if game.pile[player]:
                card = game.pile[player].pop()
                recap += f'\n{card.name}'

        return recap
mine = Mine(name="Mine", cost=4, points=4, text="4:4, Oust the top 4 cards of your discard pile")
class DinosaurBones(Card):
    def play(self, player, game, index, bonus):
        for _ in range(6):
            game.pile[player].append(broken_bone)

        return super().play(player, game, index, bonus)
dinosaur_bones = DinosaurBones(name="Dinosaur Bones", cost=4, points=6, qualities=[Quality.FLEETING],
                             text="4:6, becomes 6x 1:0 fleeting bones after resolving")
class StoneGolem(Card):
    def __init__(self, points):
        text = f"5:{points}, permanently grows by +1 after playing"
        super().__init__("Stone Golem", cost=5, points=points, qualities=[Quality.FLEETING],
                         text=text, dynamic_text=text)

    def play(self, player, game, index, bonus):
        new_golem = StoneGolem(self.points + 1)
        game.pile[player].append(new_golem)

        return super().play(player, game, index, bonus)
stone_golem = StoneGolem(5)
class Atlas(Card):
    def get_cost(self, player, game):
        if not game.pile[player] and not game.deck[player]:
            return 0
        else:
            return self.cost
atlas = Atlas(name="Atlas", cost=7, points=7, text="7:7, costs 0 if your deck and pile are empty")
uluru = Card(name="Uluru", cost=10, points=15, text="10:15")


"""Other"""
class Paranoia(SightCard):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(paranoia, game, player)
paranoia = Paranoia(name="Paranoia", cost=2, qualities=[Quality.FLEETING], text="2: vision, fleeting, create a new paranoia in hand")
class RaiseDead(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if game.pile[player]:
            card = game.pile[player].pop()
            game.deck[player].append(card)

            recap += f'\nRaise {card.name}'

        return recap
raise_dead = RaiseDead(name="Raise Dead", cost=2, points=2, text="2:2 put the top card of your pile on top of deck")
class Lock(Card):
    def on_play(self, player, game):
        game.priority ^= 1
lock = Lock(name="Lock", cost=3, points=3, text="3:3, keep priority")
class Spectre(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(haunt, game, player^1)
spectre = Spectre(name="Spectre", cost=3, points=3, text="4:4, create a 1:0 in opponent's hand")
class Spy(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(camera, game, player ^ 1)
spy = Spy(name="Spy", cost=1, text="1: create a 2:0 camera in opponent's hand which gives you vision each upkeep")


"""TOKENS"""
haunt = Card(name="Haunt", cost=1, qualities=[Quality.VISIBLE, Quality.FLEETING], text="1:0, fleeting")
class Camera(Card):
    def on_upkeep(self, player, game):
        game.vision[player^1] = True
camera = Camera(name="Camera", cost=2, qualities=[Quality.FLEETING],
                text="2:0, fleeting, gives vision at your upkeep")
broken_bone = Card(name="Broken Bone", cost=1, qualities=[Quality.FLEETING], text="1:0, fleeting")
robot = Card(name='Robot', qualities=[Quality.FLEETING], text=f'0:X, fleeting')

tokens = [haunt, camera, broken_bone, robot]

"""SCRAPS"""
dragon_spring = Card(name="Dragon", qualities=[Quality.FLEETING], text="7:6, visible, spring")
dragon = Card(name="Dragon", cost=6, points=7, qualities=[Quality.VISIBLE], text="7:6, visible, spring", spring=dragon_spring)

full_catalog = [rat, cat, swan, cow, gorilla, elephant, dino, hurricane,
             ember, dash,  firewall, charcoal, kindle, force, burning_skull, volcano,
             stork, dove, twitter, owl, nest, vulture, peace, pelican, phoenix, ostrich,
             snake_egg, ouroboros, serpent, salamander, temptation, sand_snake, frog_prince, wyvern, cobra,
             stars, cosmos,
             shoot, stump, roots, sprout, fruiting, pine, bulb, lotus, leaf_swirl, pollen, oak,
             maat, bone_knife, robe, cultist, imprison, gift, stalker, carnivore, kenku, nightmare,
             star_fish, flying_fish, perch, dolphin, angler, piranha, school_of_fish, whale, squid,
             raft, figurehead, crows_nest, fishing_boat, drakkar, ship_wreck, trireme,
             paranoia, raise_dead, lock, spectre, spy,
             drone, cog, gears, factory, anvil, cogsplosion, ai, sine, foundry,
             crossed_bones, dig, mine, gnaw, dinosaur_bones, stone_golem, atlas, uluru]
non_collectibles = [hidden_card] + tokens
all_cards = full_catalog + non_collectibles
