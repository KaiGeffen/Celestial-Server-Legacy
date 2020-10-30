from logic.Card import *
from logic.Effects import Status, Quality
from logic.Story import Source

"""FIRE"""
class Ember(Card):
    def play(self, player, game, index, bonus):
        if game.score[player] == 0:
            bonus += 1

        return super().play(player, game, index, bonus)
ember = Ember(name="Ember", text="0:0, +1 if you have 0 points")
dash = FireCard(name="Dash", cost=2, points=3, text="2:3, flare (Worth 1 less for every card before it)")
class Firewall(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.counter(game)

        return recap
firewall = Firewall(name="Firewall", cost=2, text="2:0, counter the next card this round")
class Portal(Card):
    def play(self, player, game, index, bonus):
        result = super().play(player, game, index, bonus)

        index_final_owned_card = -1
        index = 0
        for act in game.story.acts:
            if act.owner == player:
                index_final_owned_card = index

            index += 1

        if index_final_owned_card > 0:
            act = game.story.move_act(index_final_owned_card, 0)
            result += f'\n{act.card.name} move {index_final_owned_card}'

        return result
portal = Portal(name="Portal", cost=2, points=2, text="2:2, your last card this round moves to immediately after Portal in the story")
class Charcoal(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.oust(1, game, player)
        return  recap
charcoal = Charcoal(name="Charcoal", cost=3, points=4, text="3:4, oust (Remove from the game) the lowest card in your hand")
class Haze(Card):
    def play(self, player, game, index, bonus):
        def is_cost_3(act):
            return act.card.cost == 3

        recap = super().play(player, game, index, bonus)

        recap += self.counter(game, is_cost_3)

        return recap
haze = Haze(name="Haze", cost=3, points=3, qualities=[Quality.VISIBLE], text="3:3, visible, counter the next 3-cost card this round")
class Kindle(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for player in (0, 1):
            recap += self.discard(1, game, player)

        return recap
kindle = Kindle(name="Kindle", cost=3, points=3, text="3:3, both players discard 1 (Their leftmost card from hand)")
force = FireCard(name="Force", cost=5, points=6, text="5:6, flare (Worth 1 less for every card before it)")
class FireRing(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.counter(game)
        recap += self.counter(game)

        return recap
fire_ring = FireRing(name="Fire Ring", cost=5, text="5:0, counter the next 2 cards this round")
class Ifrit(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus) + '\nOppress'

        for act in game.story.acts:
            act.bonus -= 1

        return recap
ifrit = Ifrit(name="Ifrit", cost=8, points=7, text="8:7, later cards this round are worth -1")


"""BIRD"""
dove = Card(name="Dove", cost=1, points=1, qualities=[Quality.VISIBLE, Quality.FLEETING], text="1:1, visible, fleeting (After resolving, this card is removed from the game instead of moving to your discard pile)")
class Twitter(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus) + '\nInspirit'

        for act in game.story.acts:
            act.bonus += 1

        return recap
twitter = Twitter(name="Twitter", cost=1, qualities=[Quality.VISIBLE], text="1:0, later cards this round are worth +1")
class Owl(SightCard):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.flock(1, game, player)
owl = Owl(name="Owl", cost=1, text="1:0, flock 1 (After your next draw step, add 1 Dove to your hand), sight (This round the story is visible to you)")
nest = FlockCard(name="Nest", amt=3, cost=2, points=1, text="2:1, flock 3 (After your next draw step, add 3 Doves to your hand.)")
class Swift(Card):
    def play(self, player, game, index, bonus):
        if not game.story.is_empty():
            if game.story.acts[0].card.cost == 1:
                bonus += 1

        return super().play(player, game, index, bonus)
swift = Swift(name="Swift", cost=2, points=2, qualities=[Quality.VISIBLE], text="2:2, visible, if the next card costs 1, +1")
class Peace(Card):
    def play(self, player, game, index, bonus):
        for act in game.story.acts:
            if act.card is dove:
                return super().play(player, game, index, bonus) + self.reset(game)

        return super().play(player, game, index, bonus)
peace = Peace(name="Peace", cost=3, points=3, qualities=[Quality.VISIBLE], text="3:3, visible, reset if a dove is later this round")
class Vulture(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.dig(1, game, player)
        recap += self.flock(1, game, player)

        return  recap
vulture = Vulture(name="Vulture", cost=3, points=3, text="3:3, flock 1, oust the top card of your pile")
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
phoenix = FlockCard(name="Phoenix", amt=1, cost=5, points=5, qualities=[Quality.VISIBLE], text="5:5, visible, flock 1")
class Ostrich(Card):
    def get_cost(self, player, game):
        amt = 0
        for card in game.hand[player]:
            if card.cost <= 1:
                amt += 1

        return 8 - amt
ostrich = Ostrich(name="Ostrich", cost=8, points=6, text="8:6, costs 1 less for each 0/1 in hand")
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


"""SNAKE"""
class Swamp(Card):
    def play(self, player, game, index, bonus):
        for act in game.story.acts:
            if act.owner == player and act.source is Source.SPRING:
                return act.card.play_spring(player, game, index, bonus)

        return super().play(player, game, index, bonus)
swamp = Swamp(name="Swamp", cost=0, text="0:0, copy the effect of your first sprung card in the story")
class Snake_Egg(Card):
    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus)

        recap += self.draw(1, game, player)

        return recap
snake_egg = Snake_Egg(name="Snake Egg", cost=1, points=1, text="1:1, spring: 1 point, draw 1", spring=True)
class Ouroboros(Card):
    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus - self.points)

        recap += self.oust(2, game, player)
        recap += self.draw(2, game, player)

        return recap
ouroboros = Ouroboros(name="Ouroboros", cost=2, points=2, text="2:2, spring: oust 2, draw 2", spring=True)
class SnakeEye(SightCard):
    def play(self, player, game, index, bonus):
        amt = 0
        if game.story.get_length() > 0:
            if player == game.story.acts[-1].owner:
                amt += 3

        return super().play(player, game, index, bonus + amt)
snake_eye = SnakeEye(name="Snake Eye", cost=2, points=0, qualities=[Quality.VISIBLE],
                     text="2:0, visible, sight, +3 if the final card this round is yours (Not counting this)")
class Serpent(Card):
    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus - self.points)

        recap += self.discard(1, game, player ^ 1)

        return recap
serpent = Serpent(name="Serpent", cost=3, points=3, text="3:3, spring: opponent discards 1 (The leftmost card in their hand)", spring=True)
class SnakeSpiral(Card):
    def on_play(self, player, game):
        if game.hand[player]:
            first_card = game.hand[player].pop(0)
            game.hand[player].append(first_card)
snake_spiral = SnakeSpiral(name="Snake Spiral", cost=3, points=3,
                           text="3:3. When played, move the first card in your hand to the last position.")
class Salamander(FireCard):
    def play_spring(self, player, game, index, bonus):
        return self.play(player, game, index, bonus)
salamander = Salamander(name="Salamander", cost=4, points=4, text="4:4, flare, spring: 4 points, flare", spring=True)
class Temptation(Card):
    def play_spring(self, player, game, index, bonus):
        return self.play(player, game, index, bonus - self.points) + self.nourish(1, game, player)
temptation = Temptation(name="Temptation", cost=5, points=5, text="5:5, spring: nourish 1", spring=True)
class FrogPrince(Card):
    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus - self.points)

        recap += self.inspire(1, game, player)

        return recap
frog_prince = FrogPrince(name="Frog Prince", cost=6, points=6, text="6:6, spring: inspire 1", spring=True)
class Wyvern(Card):
    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus - self.points)

        recap += self.flock(3, game, player)

        return recap
wyvern = Wyvern(name="Wyvern", cost=7, points=7, text="7:7, spring: flock 3", spring=True)
class Cobra(Card):
    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus - self.points)

        recap += self.tutor(2, game, player)

        return recap
cobra = Cobra(name="Cobra", cost=8, points=9, text="8:9, spring: tutor a 2", spring=True)


"""Discard"""
class BoneKnife(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(1, game, opp)
bone_knife = BoneKnife(name="Bone Knife", text="0:0, opponent discards 1")
class Mute(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.restrict(1, game, player ^ 1)
mute = Mute(name="Mute", cost=1, points=1, text="1:1, restrict 1 (Your opponent can't play their leftmost unrestricted card next turn)")
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
cultist = Cultist(name="Cultist", cost=2, text="2:0, opponent discards 1, tutor an 8")
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
class Carnivore(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        if game.hand[opp]:
            if game.hand[opp][0].cost <= 1:
                bonus += 1

        return super().play(player, game, index, bonus) + self.discard(1, game, opp)
carnivore = Carnivore(name="Carnivore", cost=4, points=3, text="4:3, opponent discards 1, +1 if that card costs 0 or 1")
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
kenku = Kenku(name="Kenku", cost=6, points=5, text="6:5, oust each 0 or 1 cost card from your hand, opponent discards 1 for each")
class Nightmare(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(2, game, opp)
nightmare = Nightmare(name="Nightmare", cost=8, points=5, text="8:5, opponent discards 2")


"""Machines"""
class Cog(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(1, game, player)
cog = Cog(name="Cog", cost=0, text="0:0, build 1 (+1 to a robot in your hand, or make a 0:1 fleeting robot)")
class Drone(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(0, game, player)
        return  recap
drone = Drone(name="Drone", cost=1, text="1:0, tutor a 0")
class Gears(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(2, game, player)
gears = Gears(name="Gears", cost=2, text="2:0, build 2")
class Factory(Card):
    def play(self, player, game, index, bonus):
        amt = game.story.get_length()
        return super().play(player, game, index, bonus) + self.build(amt, game, player)
factory = Factory(name="Factory", cost=3, text="3:0, build X, where X is number of cards later in the story")
class Anvil(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(2, game, player)
anvil = Anvil(name="Anvil", cost=4, points=3, text="4:3, build 2")
class Cogsplosion(Card):
    def play(self, player, game, index, bonus):
        index = -1
        for card in game.hand[player]:
            index += 1

            if card.name == 'Robot':
                bonus += card.points

                return super().play(player, game, index, bonus) + self.discard(1, game, player, index=index)

        return ''
cogsplosion = Cogsplosion(name="Cogsplosion", cost=4, text="4:X, discard your first 0/X robot")
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
class Foundry(Card):
    def play(self, player, game, index, bonus):
        amt = index
        bonus -= amt

        recap = super().play(player, game, index, bonus)
        recap += self.build(amt, game, player)

        return recap
foundry = Foundry(name="Foundry", cost=5, points=5, text="5:5-X, build X, where X is cards in story before this card")


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
class Roots(Card):
    def play(self, player, game, index, bonus):
        your_last_card_cost = self.cost
        for act in game.story.acts:
            if act.owner == player:
                your_last_card_cost = act.card.cost

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
sprout = Sprout(name="Sprout", cost=2, text="2:0, inspire, tutor a 4")
class Fruiting(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(3, game, player)
fruiting = Fruiting(name="Fruiting", cost=3, text="3:0, nourish 3 (Your next card gives +3 points)")
class Pine(Card):
    def play(self, player, game, index, bonus):
        if self.your_final(game, player):
            bonus += 2

        return super().play(player, game, index, bonus) + self.gentle(game, player)
pine = Pine(name="Pine", cost=4, points=2, text="4:2, gentle, final: +2")
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
lotus = Lotus(name="Lotus", cost=5, text="5:0, inspire 2, final: reset")
class LeafSwirl(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if self.your_final(game, player):
            amt = len(game.hand[player])
            recap += self.oust(amt, game, player)
            recap += self.draw(amt, game, player)

        return recap
leaf_swirl = LeafSwirl(name="Leaf Swirl", cost=5, points=5, text="5:5, final: oust your hand, draw that many cards")
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
oak = Oak(name="Oak", cost=8, points=8, text="8:8, gentle (If you win this round, convert to nourish any points not needed to win)")


"""Earth"""
class CrossedBones(Card):
    def play(self, player, game, index, bonus):
        for _ in range(2):
            game.pile[player].append(broken_bone)

        return super().play(player, game, index, bonus)
crossed_bones = CrossedBones(name="Crossed Bones", cost=1, points=2, qualities=[Quality.FLEETING],
                             text="1:2, becomes 2x 1:0 fleeting broken bones after resolving")
class Dig(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.dig(2, game, player)

        return recap
dig = Dig(name="Dig", cost=2, points=2, text="2:2, oust the top 2 cards of your discard pile")
class Gnaw(Card):
    def play(self, player, game, index, bonus):
        for act in game.story.acts:
            if act.card is broken_bone:
                bonus += 3
                break

        return super().play(player, game, index, bonus)
gnaw = Gnaw(name="Gnaw", cost=3, points=3, qualities=[Quality.VISIBLE], text="3:3, visible, +3 if there is a broken bone in story")
class Mine(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.dig(4, game, player)

        return recap
mine = Mine(name="Mine", cost=4, points=4, text="4:4, oust the top 4 cards of your discard pile")
class DinosaurBones(Card):
    def play(self, player, game, index, bonus):
        for _ in range(3):
            game.pile[player].append(broken_bone)

        return super().play(player, game, index, bonus)
dinosaur_bones = DinosaurBones(name="Dinosaur Bones", cost=4, points=5, qualities=[Quality.FLEETING],
                             text="4:5, becomes 3x 1:0 fleeting broken bones after resolving")
class Wolf(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(broken_bone, game, player^1)
wolf = Wolf(name="Wolf", cost=4, points=4, text="4:4, create a 1:0 fleeting broken bone in opponent's hand")
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
class Boar(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for card in game.hand[player^1]:
            if card is broken_bone:
                recap += self.tutor(6, game, player)

        return recap
boar = Boar(name="Boar", cost=6, points=6, qualities=[Quality.VISIBLE], text="6:6, visible, tutor 6 once for each broken bone in opponent's hand")
class Atlas(Card):
    def get_cost(self, player, game):
        if not game.pile[player] and not game.deck[player]:
            return 0
        else:
            return self.cost
atlas = Atlas(name="Atlas", cost=7, points=7, text="7:7, costs 0 if your deck and pile are empty")
uluru = Card(name="Uluru", cost=10, points=15, text="10:15")


"""Fish"""
flying_fish = FlowCard(name="Flying Fish", cost=1, points=1, text="1:1, flow (As soon as you ebb, cycle this)")
class StarFish(FlowCard):
    def on_flow(self, player, game):
        self.add_mana(1, game, player)
        return super().on_flow(player, game)
star_fish = StarFish(name="Star Fish", cost=1, text="1:0, flow: Gain 1 mana")
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
class Angler(FlowCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(1, game, player)

        return recap
angler = Angler(name="Angler", cost=4, points=4, qualities=[Quality.VISIBLE], text="4:4, flow, visible, tutor a 1")
class Piranha(FlowCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.counter(game)

        return recap
piranha = Piranha(name="Piranha", cost=4, points=1, text="4:1, flow, counter the next card this round")
class SchoolOfFish(FlowCard):
    def get_cost(self, player, game):
        amt = 0
        for act in game.story.acts:
            if act.owner == player and act.card.cost == 1:
                amt += 1

        return self.cost - amt
school_of_fish = SchoolOfFish(name="School of Fish", cost=5, points=5, text="5:5, flow, costs 1 less for each 1-cost you have in story")
class Whale(FlowCard):
    def get_cost(self, player, game):
        amt = 0
        for card in game.hand[player]:
            if card.cost == 1:
                amt += 1

        return self.cost - amt
whale = Whale(name="Whale", cost=8, points=7, text="8:7, flow, costs 1 less for each 1-cost in your hand")
class Wave(FlowCard):
    def on_flow(self, player, game):
        self.nourish(1, game, player)
        return super().on_flow(player, game)
wave = Wave(name="Wave", cost=9, points=9, text="9:9, flow: Nourish 1")


"""Ships"""
class Figurehead(EbbCard):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.inspire(1, game, player)
figurehead = Figurehead(name="Figurehead", cost=1, text="1:0, ebb, inspire 1")
class FishingBoat(EbbCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for i in range(3):
            recap += self.tutor(1, game, player)

        return recap
fishing_boat = FishingBoat(name="Fishing Boat", cost=2, text="2:0, ebb, tutor a 1 3 times")
drakkar = EbbCard(name="Drakkar", cost=3, points=3, text="3:3, ebb")
class ShipWreck(EbbCard):
    def get_cost(self, player, game):
        opp = (player + 1) % 2
        amt = game.wins[opp] - game.wins[player]

        return self.cost - amt
ship_wreck = ShipWreck(name="Ship Wreck", cost=4, points=3,
                       text="4:3, ebb, costs 1 less for each round-win you are behind by (Cost more if you are ahead)")
trireme = EbbCard(name="Trireme", cost=5, points=5, text="5:5, ebb")
warship = EbbCard(name="Warship", cost=7, points=7, text="7:7, ebb")


"""Death"""
class Undead(Card):
    def pile_upkeep(self, player, game, index):
        cost = self.get_cost(player, game)
        if game.mana[player] >= cost:

            # Attempt to discard a card, if you can, play this card
            if self.discard(1, game, player):
                # Play this card for its cost
                game.mana[player] -= cost
                game.story.add_act(self, player, Source.PILE)

                # Remove this card from the pile
                game.pile[player].pop(index)

                # Return that a card left the pile
                return True

        return False

class Graveyard(Card):
    def play(self, player, game, index, bonus):
        for p in (player, player ^ 1):
            if len(game.pile[p]) >= 6:
                bonus += 1

        return super().play(player, game, index, bonus)
graveyard = Graveyard(name="Graveyard", cost=0, points=0, text="0:0, +1 for each player with 6 or more cards in pile")
zombie = Undead(name="Zombie", cost=0, points=1, qualities=[Quality.VISIBLE], text="0:1, visible, undead (on upkeep, if this is in pile and you have the mana, discard 1 to play this card)")
class Drown(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.mill(3, game, player)
drown = Drown(name="Drown", cost=1, points=1, text="1:1, mill yourself 3 (Top 3 cards of deck go to pile)")
class RaiseDead(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if game.pile[player]:
            card = game.pile[player].pop()
            game.deck[player].append(card)

            recap += f'\nRaise {card.name}'

        return recap
raise_dead = RaiseDead(name="Raise Dead", cost=2, points=2, text="2:2 put the top card of your pile on top of deck")
haunt = Undead(name="Haunt", cost=3, points=3, qualities=[Quality.VISIBLE], text="3:3, visible, undead (on upkeep, if this is in pile and you have the mana, discard 1 to play this card)")
spectre = Undead(name="Spectre", cost=5, points=5, qualities=[Quality.VISIBLE], text="5:5, visible, undead (on upkeep, if this is in pile and you have the mana, discard 1 to play this card)")
class Tumulus(Card):
    def play(self, player, game, index, bonus):
        if len(game.pile[player]) >= 8:
            bonus += 2

        return super().play(player, game, index, bonus)
tumulus = Tumulus(name="Tumulus", cost=5, points=4, text="5:4, +2 if your pile has at least 8 cards in it")
class Prayer(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.reset(game)
        recap += self.inspire(1, game, player)

        return recap

    def pile_upkeep(self, player, game, index):
        self.add_mana(1, game, player)
        game.status[player].append(Status.STARVE)

        return False
prayer = Prayer(name="Prayer", cost=5,
                text="5:0, reset. On upkeep while in pile, +1 mana and starve 1 (Your next card gives -1 point)")

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

            return super().play(player, game, index, bonus) + f"\nTop: {card.name}"
        else:
            return super().play(player, game, index, bonus)
sarcophagus = Sarcophagus(name="Sarcophagus", cost=6,
                text="6:X, put the highest cost card from your pile on top of your deck, X is its cost")
class Reaper(Card):
    def get_cost(self, player, game):
        amt = 0

        for act in game.story.acts:
            if act.owner == player and act.source == Source.PILE:
                amt += 1

        return self.cost - amt
reaper = Reaper(name="Reaper", cost=6, points=6, text="6:6, costs 1 less for each card you played from pile this round")
class Anubis(Card):
    def get_cost(self, player, game):
        if len(game.pile[player]) >= 12:
            return 0
        else:
            return self.cost
anubis = Anubis(name="Anubis", cost=7, points=7, text="7:7, costs 0 if you have at least 12 cards in your pile")


"""Other"""
class Hurricane(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.reset(game)
hurricane = Hurricane(name="Hurricane", cost=4, text="4:0, reset")
class Lock(Card):
    def on_play(self, player, game):
        game.priority ^= 1
lock = Lock(name="Lock", cost=3, points=3, text="3:3, keep priority")
class Spy(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(camera, game, player ^ 1)
spy = Spy(name="Spy", cost=1, text="1:0, create a 2:0 camera in opponent's hand which gives you sight each upkeep")
# class Wave(Card):
#     def get_cost(self, player, game):
#         high_score = 0
#         current_score = 0
#         for act in game.story.acts:
#             if act.owner == player:
#                 current_score += 1
#             else:
#                 current_score = 0
#
#             if current_score > high_score:
#                 high_score = current_score
#
#         return self.cost - high_score
# wave = Wave(name="Wave", cost=7, points=6,
#             text="7:6, costs X less where X is the length of your longest chain in the story (Chain is cards in sequence)")



"""Tokens"""
class Camera(Card):
    def on_upkeep(self, player, game):
        game.vision[player^1] = True
camera = Camera(name="Camera", cost=2, qualities=[Quality.FLEETING],
                text="2:0, fleeting, gives sight to your opponent during your upkeep")
broken_bone = Card(name="Broken Bone", cost=1, qualities=[Quality.FLEETING], text="1:0, fleeting")
robot = Card(name='Robot', qualities=[Quality.FLEETING], text="0:X, fleeting")


tokens = [camera, broken_bone, robot]


"""Lists"""
hidden_card = Card(name="Cardback", cost=0, points=0, text="?")
full_catalog = [
    ember, dash, firewall, portal, charcoal, kindle, haze, force, fire_ring, ifrit,
    dove, twitter, owl, nest, swift, peace, pelican, phoenix, icarus,
    swamp, snake_egg, ouroboros, snake_eye, serpent, snake_spiral, salamander, temptation, frog_prince, wyvern, cobra,
    stars, cosmos, roots, sprout, fruiting, pine, bulb, lotus, leaf_swirl, pollen, oak,
    bone_knife, mute, cultist, imprison, gift, stalker, carnivore, kenku, nightmare,
    flying_fish, star_fish, perch, angler, piranha, school_of_fish, whale, wave,
    figurehead, fishing_boat, drakkar, ship_wreck, trireme, warship,
    cog, drone, gears, factory, anvil, cogsplosion, ai, sine, foundry,
    crossed_bones, dig, gnaw, mine, dinosaur_bones, wolf, stone_golem, boar, atlas, uluru,
    graveyard, zombie, drown, raise_dead, haunt, spectre, prayer, tumulus, sarcophagus, anubis,
    hurricane, lock, spy
]
# A list of simple cards, so that new players aren't overwhelmed
vanilla_catalog = [
    ember, dash, firewall, portal, charcoal, kindle, haze, force, fire_ring, ifrit,
    dove, twitter, owl, nest, swift, peace, pelican, phoenix, icarus,
    crossed_bones, dig, gnaw, mine, dinosaur_bones, wolf, stone_golem, boar, atlas, uluru,
    bone_knife, hurricane, pollen
]
# full_catalog = vanilla_catalog

non_collectibles = [hidden_card] + tokens
all_cards = full_catalog + non_collectibles



import random

# Get a random deck for the computer opponent
def get_computer_deck():
    possible_cards = [
        [crossed_bones],
        [swift, ouroboros],
        [kindle, gift, gnaw],
        [pelican, angler, wolf],
        [phoenix, stone_golem, school_of_fish, tumulus],
        [frog_prince, boar],
        [wyvern],
        [cobra, ifrit, nightmare]
    ]
    distribution = [3, 2, 3, 3, 2, 1, 0, 1]
    deck = []
    for i in range(len(possible_cards)):
        for _ in range(distribution[i]):
            deck.append(random.choice(possible_cards[i]))

    return deck
