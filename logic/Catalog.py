from logic.Card import *
from logic.Effects import Status, Quality
from logic.Story import Source, Act

# TODO make a separate file for tokens
"""Tokens"""


class Camera(Card):
    def on_upkeep(self, player, game, index):
        game.vision[player ^ 1] += 4


camera = Camera(name="Camera", cost=2, qualities=[Quality.FLEETING],
                text="2:0, fleeting, at the start of each round, give your opponent vision 4")

class BrokenBone(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.BoneSnap
        return super().play(player, game, index, bonus)
broken_bone = BrokenBone(name="Broken Bone", cost=1, qualities=[Quality.FLEETING], text="1:0, fleeting")
robot = Card(name='Robot', qualities=[Quality.FLEETING], text="0:X, fleeting")


class Virus(Card):
    def pile_upkeep(self, player, game, index):
        game.status[player].append(Status.STARVE)

        return False


virus = Virus(name="Virus", cost=3, qualities=[Quality.FLEETING], pile_highlight=True,
              text="3:0, fleeting. On upkeep while in pile starve 1")


class WantedPoster(Card):
    def play(self, player, game, index, bonus):
        bonus += 2 * game.pile[player ^ 1].count(bandit)

        return super().play(player, game, index, bonus)


wanted_poster = WantedPoster(name="Wanted Poster", cost=1, qualities=[Quality.FLEETING],
                             text="1:0, fleeting, +2 for each Bandit in your opponent's discard pile")

tokens = [camera, broken_bone, robot, wanted_poster]

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


portal = Portal(name="Portal", cost=2, points=2,
                text="2:2, your last card this round moves to immediately after Portal in the story")


class Charcoal(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        # recap += self.oust(1, game, player)
        recap += self.discard(1, game, player)

        return recap


charcoal = Charcoal(name="Charcoal", cost=3, points=4, qualities=[Quality.VISIBLE], text="3:4, visible, discard a card")


class Haze(Card):
    def play(self, player, game, index, bonus):
        def is_cost_3(act):
            return act.card.cost == 3

        recap = super().play(player, game, index, bonus)

        recap += self.counter(game, is_cost_3)

        return recap


haze = Haze(name="Haze", cost=3, points=3, qualities=[Quality.VISIBLE],
            text="3:3, visible, counter the next 3-cost card this round")


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


class Distraction(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        amt = game.mana[player]
        recap += self.flock(amt, game, player)

        game.mana[player] = 0

        return recap


distraction = Distraction(name="Distraction", cost=4, points=4,
                          text="4:4, spend all your unspent mana to flock that much")
class Dove(Card):
    def play(self, player, game, index, bonus):
        game.sound_effect = SoundEffect.Bird
        return super().play(player, game, index, bonus)
dove = Dove(name="Dove", cost=1, points=1, qualities=[Quality.VISIBLE, Quality.FLEETING],
            text="1:1, visible, fleeting (After resolving, this card is removed from the game instead of moving to your discard pile)")


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


owl = Owl(amt=4, name="Owl", cost=1,
          text="1:0, flock 1 (After your next draw step, add 1 Dove to your hand), sight 4 (This round the first 4 cards of story are visible to you)")
nest = FlockCard(name="Nest", amt=3, cost=2, points=1,
                 text="2:1, flock 3 (After your next draw step, add 3 Doves to your hand.)")


class Swift(Card):
    def play(self, player, game, index, bonus):
        if not game.story.is_empty():
            if game.story.acts[0].card.cost == 1:
                bonus += 1

        return super().play(player, game, index, bonus)


swift = Swift(name="Swift", cost=2, points=2, qualities=[Quality.VISIBLE],
              text="2:2, visible, if the next card costs 1, +1")


class Peace(Card):
    def play(self, player, game, index, bonus):
        for act in game.story.acts:
            if act.card is dove:
                return super().play(player, game, index, bonus) + self.reset(game)

        return super().play(player, game, index, bonus)


peace = Peace(name="Peace", cost=3, points=3, qualities=[Quality.VISIBLE],
              text="3:3, visible, reset if a dove is later this round")


class Vulture(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.oust(1, game, player)
        recap += self.draw(1, game, player)

        return recap


vulture = Vulture(name="Vulture", cost=3, points=3, text="3:3, oust 1, draw 1")


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


class Cuauhtli(SightCard):
    def on_play(self, player, game):
        game.hand[player] = [dove] * len(game.hand[player])

        super().on_play(player, game)

    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(2, game, player)


cuauhtli = Cuauhtli(amt=4, name="Cuauhtli", cost=6, points=6,
                    text="6:6, nourish 2. When played, gain sight 4 and transform each card in your hand into a Dove.")

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


snake_eye = SnakeEye(amt=3, name="Snake Eye", cost=2, points=0, qualities=[Quality.VISIBLE],
                     text="2:0, visible, sight 3, +3 if the final card this round is yours (Not counting this)")


class Serpent(Card):
    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus - self.points)

        recap += self.discard(1, game, player ^ 1)

        return recap


serpent = Serpent(name="Serpent", cost=3, points=3,
                  text="3:3, spring: opponent discards 1 (The leftmost card in their hand)", spring=True)


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


class Turtle(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.safe(2, game, player)

        return recap

    def play_spring(self, player, game, index, bonus):
        recap = super().play_spring(player, game, index, bonus - self.points)

        return recap


turtle = Turtle(name="Turtle", cost=4, points=2, text="4:2, safe 2, spring: safe 2", spring=True)

"""Discard"""


class BoneKnife(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(1, game, opp)


bone_knife = BoneKnife(name="Bone Knife", text="0:0, opponent discards 1")


class Mute(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.restrict(1, game, player ^ 1)


mute = Mute(name="Mute", cost=1, points=1,
            text="1:1, restrict 1 (Your opponent can't play their leftmost unrestricted card next turn)")


class Robe(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        bonus -= len(game.hand[opp])

        return super().play(player, game, index, bonus)


robe = Robe(name="Robe", cost=1, points=3, text="1:3, -1 for each card in opponent's hand")


class Cultist(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2

        recap = super().play(player, game, index, bonus)
        recap += self.discard(1, game, opp)
        recap += self.tutor(8, game, player)

        return recap


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


kenku = Kenku(name="Kenku", cost=6, points=5,
              text="6:5, oust each 0 or 1 cost card from your hand, opponent discards 1 for each")


class Nightmare(Card):
    def play(self, player, game, index, bonus):
        opp = (player + 1) % 2
        return super().play(player, game, index, bonus) + self.discard(2, game, opp)


nightmare = Nightmare(name="Nightmare", cost=8, points=6, text="8:6, opponent discards 2")

"""Machines"""


class Cog(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.build(1, game, player)


cog = Cog(name="Cog", cost=0, text="0:0, build 1 (+1 to a robot in your hand, or make a 0:1 fleeting robot)")


class Drone(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.tutor(0, game, player)
        return recap


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
        return recap


roots = Roots(name="Roots", cost=1, points=1, text="1:1, +1 if your final card costs 4+")


class Sprout(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.inspire(1, game, player)
        recap += self.tutor(4, game, player)
        return recap


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


oak = Oak(name="Oak", cost=8, points=8,
          text="8:8, gentle (If you win this round, convert to nourish any points not needed to win)")


# Maybe something while in pile? Cost reduction?
class Baobab(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.gentle(game, player)


baobab = Baobab(name="Baobab", cost=10, points=8,
                text="10:10, gentle (If you win this round, convert to nourish any points not needed to win)")


class Cornucopia(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if game.story.acts:
            game.story.acts[0].bonus += 1

            recap += f"\n<{game.story.acts[0].card.name}>"

        return recap


cornucopia = Cornucopia(name="Cornucopia", cost=2, points=2, qualities=[Quality.VISIBLE],
                        text="2:2, visible, the next card this round is worth +1")

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


gnaw = Gnaw(name="Gnaw", cost=3, points=3, qualities=[Quality.VISIBLE],
            text="3:3, visible, +3 if there is a broken bone in story")


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


class Wolf(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(broken_bone, game, player ^ 1)


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

        for card in game.hand[player ^ 1]:
            if card is broken_bone:
                recap += self.tutor(6, game, player)

        return recap


boar = Boar(name="Boar", cost=6, points=6, qualities=[Quality.VISIBLE],
            text="6:6, visible, tutor 6 once for each broken bone in opponent's hand")


class Atlas(Card):
    def get_cost(self, player, game):
        if not game.pile[player] and not game.deck[player]:
            return 0
        else:
            return self.cost


atlas = Atlas(name="Atlas", cost=7, points=7, text="7:7, costs 0 if your deck and pile are empty")
uluru = Card(name="Uluru", cost=10, points=15, text="10:15")


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


school_of_fish = SchoolOfFish(name="School of Fish", cost=5, points=5,
                              text="5:5, flow, costs 1 less for each 1-cost you have in story")


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


class Crab(FlowCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.safe(3, game, player)

        return recap


crab = Crab(name="Crab", cost=2,
            text="2:0, flow, safe 3 (If you would lose the round by 3 or fewer points, instead the round is a draw)")

"""Ships"""


class Figurehead(EbbCard):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.inspire(1, game, player)


figurehead = Figurehead(name="Figurehead", cost=1, text="1:0, ebb, inspire 1")


class FishingBoat(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for i in range(3):
            recap += self.tutor(1, game, player)

        return recap


fishing_boat = FishingBoat(name="Fishing Boat", cost=2, text="2:0, tutor a 1 3 times")
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
    def __init__(self, **kwargs):
        super().__init__(pile_highlight=True, **kwargs)

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
zombie = Undead(name="Zombie", cost=0, points=1, qualities=[Quality.VISIBLE],
                text="0:1, visible, undead (on upkeep, if this is in pile and you have the mana, discard 1 to play this card)")


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
haunt = Undead(name="Haunt", cost=3, points=3, qualities=[Quality.VISIBLE],
               text="3:3, visible, undead (on upkeep, if this is in pile and you have the mana, discard 1 to play this card)")
spectre = Undead(name="Spectre", cost=5, points=5, qualities=[Quality.VISIBLE],
                 text="5:5, visible, undead (on upkeep, if this is in pile and you have the mana, discard 1 to play this card)")


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
        # recap += self.inspire(1, game, player)

        return recap

    def pile_upkeep(self, player, game, index):
        self.add_mana(1, game, player)
        game.status[player].append(Status.STARVE)

        return False


prayer = Prayer(name="Prayer", cost=5, pile_highlight=True,
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


class Carrion(Card):
    def pile_upkeep(self, player, game, index):
        game.pile[player].append(broken_bone)

        return False


carrion = Carrion(name="Carrion", cost=3, points=3, pile_highlight=True,
                  text="3:3. On upkeep while in pile, create a 1:0 fleeting broken bone")


class Maggot(Card):
    def pile_upkeep(self, player, game, index):
        if index > 0:
            game.pile[player].pop(index - 1)
            return True
        else:
            return False


maggot = Maggot(name="Maggot", cost=0, points=0, pile_highlight=True,
                text="0:0. On upkeep while in pile, oust the card below Maggot")

"""Sun"""


class Sunflower(Card):
    def play(self, player, game, index, bonus):
        bonus += game.mana[player]
        game.mana[player] = 0

        return super().play(player, game, index, bonus)


sunflower = Sunflower(name="Sunflower", cost=1, points=0,
                      text="1:0, spend all your unspent mana to gain that many points")


class SunPriest(Card):
    def play(self, player, game, index, bonus):
        if game.mana[player] > 0:
            bonus += 1

        return super().play(player, game, index, bonus)


sun_priest = SunPriest(name="Sun Priest", cost=1, points=1, text="1:1, +1 if you have unspent mana")


class SolarExplosion(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.add_mana(1, game, player)

        return recap


solar_explosion = SolarExplosion(name="Solar Explosion", cost=2, points=2, text="2:2, gain 1 mana this turn")


class Sunlight(SightCard):
    def play(self, player, game, index, bonus):
        bonus += game.status[player].count(Status.INSPIRED)

        return super().play(player, game, index, bonus)


sunlight = Sunlight(amt=4, name="Sunlight", cost=2, points=0,
                    text="2:X, sight4, X is how much you are inspired (How much mana you've gained this turn)")


class SolarSystem(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        amt = game.mana[player]
        for act in game.story.acts:
            if act.card.cost == amt:
                act.bonus += amt

                recap += f'\n<{act.card.name}>'

                break

        return recap


solar_system = SolarSystem(name="Solar System", cost=3, points=3, qualities=[Quality.VISIBLE],
                           text="3:3, visible, X is your unspent mana. The next card this round that costs X is worth +X")


class SolarPower(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if Status.INSPIRED in game.status[player]:
            recap += self.inspire(2, game, player)

        return recap


solar_power = SolarPower(name="Solar Power", cost=3, points=2,
                         text="3:2, inspire 2 if you are inspired (If you've gained mana this turn)")


class SunCloud(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        if game.mana[player] > 0:
            recap += self.reset(game)

        return recap


sun_cloud = SunCloud(name="Sun Cloud", cost=4, points=4, text="4:4, reset if you have unspent mana")


class StarSkull(Card):
    def play(self, player, game, index, bonus):
        amt = game.mana[player]

        def cost_equals_amt(act):
            return act.card.cost == amt

        recap = super().play(player, game, index, bonus)

        recap += self.counter(game, cost_equals_amt)

        return recap


star_skull = StarSkull(name="Star Skull", cost=5, points=5, qualities=[Quality.VISIBLE],
                       text="5:5, visible, counter the next card with cost equal to your unspent mana")


class Wisdom(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if game.mana[player] > 0:
            recap += self.draw(1, game, player)

        return recap


wisdom = Wisdom(name="Wisdom", cost=5, points=4, text="5:4, draw a card if you have unspent mana")


class Eclipse(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        if game.mana[player] > 0:
            recap += self.restrict(1, game, player ^ 1)

        return recap


eclipse = Eclipse(name="Eclipse", cost=6, points=6, text="6:6, restrict 1 (opponent) if you have unspent mana")


class Sun(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.inspire(5, game, player)

        return recap


sun = Sun(name="Sun", cost=8, points=6, text="8:6, inspire 5")

"""INSECTS"""
bee = Card(name="Bee", cost=0, points=1, qualities=[Quality.VISIBLE], text="0:1, visible")
beehive = SwarmCard(name="Beehive", amt=3, cost=2,
                    text="2:0, swarm 3 (After your next draw step, add 3 Bees to your hand)")


class Butterfly(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.nourish(1, game, player)


butterfly = Butterfly(name="Butterfly", cost=1, text="1:0, nourish 1 (Your next card gives +1 points)")


class Spider(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)
        recap += self.dull(3, game, player)
        recap += self.dull(3, game, player ^ 1)

        return recap


spider = Spider(name="Spider", cost=0, text="0:0, both players dull 3 (Next turn temporarily lose 3 mana)")


class Mantis(Card):
    def play(self, player, game, index, bonus):
        if len(game.hand[player]) > 0:  # and game.hand[player][0].cost == 0:
            bonus += 3

        recap = super().play(player, game, index, bonus)

        recap += self.discard(1, game, player)

        return recap


mantis = Mantis(name="Mantis", cost=0, text="0:0, you discard a card: +3")


class Scorpion(Card):
    def play(self, player, game, index, bonus):
        def cost_below_mana(act):
            return act.card.cost < game.mana[player]

        recap = super().play(player, game, index, bonus)

        recap += self.counter(game, cost_below_mana)

        return recap


scorpion = Scorpion(name="Scorpion",
                    text="0:0, counter the next card this round which costs less than your unspent mana.")


class Honey(Card):
    def play(self, player, game, index, bonus):
        amt = game.wins[player]

        recap = super().play(player, game, index, bonus + amt)
        recap += self.swarm(amt, game, player)

        return recap


honey = Honey(name="Honey", cost=4, points=0, text="4:X, swarm X, where X is the number of rounds you have won")


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

"""RUSH"""


# TODO Use a play method in game to standardize. Also obey Restrict!
class RushCard(Card):
    def on_upkeep(self, player, game, index):
        cost = self.get_cost(player, game)
        if game.mana[player] >= cost:
            # Play this card for its cost
            game.mana[player] -= cost
            game.story.add_act(self, player, Source.PILE)
            del game.hand[player][index]

            # This card was removed from hand
            return True

        # No card was removed from hand
        return False


bull = RushCard(name="Bull", cost=1, points=2, qualities=[Quality.VISIBLE],
                text="1:2, visible, rush (If this card is in your hand during your upkeep and you have enough mana, play it)")

"""EPIC"""


class MachineApocalypse(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if index < 2:
            recap += '\nInspirit my cards'

            for act in game.story.acts:
                if act.owner == player:
                    act.bonus += 1
        elif 2 <= index < 5:
            recap += self.restrict(2, game, player ^ 1)
        else:
            recap += self.build(3, game, player)

        return recap


machine_apocalypse = MachineApocalypse(name="Machine Apocalypse", cost=2, points=0,
                                       text="""2:0, modal:
                                            0-1: Boost each of your later cards this round by 1
                                            2-4: Restrict 2
                                            5+: Build 3""")


class Crowning(Card):
    def play(self, player, game, index, bonus):
        if index < 2:
            # Covered in the on_play method
            recap = super().play(player, game, index, bonus)
        elif 2 <= index < 5:
            bonus += 1
            recap = super().play(player, game, index, bonus)
        else:
            recap = super().play(player, game, index, bonus)
            recap += self.inspire(2, game, player)

        return recap

    def on_play(self, player, game):
        if game.story.get_length() <= 1:
            game.vision[player] += 4


crowning = Crowning(name="Crowning", cost=1, points=0,
                    text="""1:0, modal:
                                            0-1: Sight 4
                                            2-4: +1 points
                                            5+: Inspire 2""")


class Nature(Card):
    def play(self, player, game, index, bonus):
        if index < 2:
            recap = super().play(player, game, index, bonus)
            recap += self.counter(game)
        elif 2 <= index < 5:
            bonus += min(2, len(game.hand[player])) * 3

            recap = super().play(player, game, index, bonus)
            recap += self.oust(2, game, player)
        else:
            recap = super().play(player, game, index, bonus)

            # Get the highest costing card from this player's deck + pile
            highest_cost_card = None
            for card in (game.deck[player] + game.pile[player]):
                if highest_cost_card is None or card.cost > highest_cost_card.cost:
                    highest_cost_card = card

            if highest_cost_card is not None:
                game.deck[player] = [highest_cost_card] * len(game.deck[player])
                game.pile[player] = [highest_cost_card] * len(game.pile[player])

            recap += f'\nSpread {highest_cost_card.name}'

        return recap


nature = Nature(name="Nature", cost=3, points=0,
                text="""3:0, modal:
                                            0-1: Counter the next card
                                            2-4: Oust 2, +3 for each
                                            5+: Change every card in your deck and pile into the highest cost card therein""")


class Desert(Card):
    def play(self, player, game, index, bonus):
        if index == 0:
            bonus += 1
            recap = super().play(player, game, index, bonus) + '\nOppressx2'

            for act in game.story.acts:
                act.bonus -= 2

        elif 1 <= index <= 2:
            recap = super().play(player, game, index, bonus)
            recap += self.reset(game)
        else:
            bonus += 4
            recap = super().play(player, game, index, bonus)

        return recap


desert = Desert(name="Desert", cost=4, points=0,
                text="""4:0, modal:
                                            0: +1, later cards this round are worth -2
                                            1-2: Reset
                                            3+: +4""")


class Privation(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        if index <= 1:
            recap += self.restrict(1, game, player ^ 1)
        elif 2 <= index <= 3:
            recap += self.discard(1, game, player ^ 1)
        else:
            recap += self.create(virus, game, player ^ 1)

        return recap


privation = Privation(name="Privation", cost=1, points=0,
                      text="""1:0, modal:
                                            0-1: Restrict 1
                                            2-3: Opponent discards 1
                                            4+: Create a 3:0 Virus in opponent's hand""")

# Opponent discards cards until the total cost is at least 3 (or something)
# 0-1: +6, nourish 3, sight 2

"""1:0 Grit
0-1: If the next card costs 2, +2
2-3: Counter your next card: +3
4+: On play, reduce the cost of each card in your hand by 1.
"""

"""2:0 Avoidance
0: Return the next card to its owners hand
1-2: +3, your opponents cards +1
3: Remove the top 3 cards of your discard pile from the game
"""

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


class Armadillo(FlowCard):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        recap += self.safe(2, game, player)

        return recap


armadillo = Armadillo(name="Armadillo", cost=1,
                      text="1:0, safe 2 (If you would lose the round by 2 or fewer points, instead the round is a draw)")


class Duality(Card):
    def play(self, player, game, index, bonus):
        recap = super().play(player, game, index, bonus)

        for act in game.story.acts:
            if act.owner == player:
                act.owner = act.owner ^ 1

                recap += f"\nSwitch {act.card.name}"

                break

        return recap


duality = Duality(name="Duality", cost=2, text="2:0, switch the owner of your next card in the story")


class Sicken(Card):
    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.create(virus, game, player ^ 1)


sicken = Sicken(name="Sicken", cost=1, text=f"1:0, create a virus in opponent's hand ({virus.text})")


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



"""Lists"""
hidden_card = Card(name="Cardback", cost=0, points=0, text="?")
full_catalog = [
    crossed_bones, spy, swift, sine, fruiting, gift, enrage, hurricane, nightmare,
    ember, dash, firewall, portal, charcoal, kindle, haze, force, fire_ring, ifrit,
    dove, twitter, paranoia, nest, swift, peace, pelican, phoenix, icarus,
    swamp, snake_egg, ouroboros, snake_eye, serpent, snake_spiral, salamander, temptation, frog_prince, wyvern, cobra,
    stars, cosmos, roots, sprout, fruiting, pine, bulb, lotus, leaf_swirl, pollen, oak,
    bone_knife, mute, cultist, imprison, gift, stalker, carnivore, kenku, nightmare,
    flying_fish, star_fish, perch, angler, piranha, school_of_fish, ecology, disintegrate,
    horus, fishing_boat, bandit, night_vision, cuauhtli, boar,
    cog, drone, gears, factory, anvil, cogsplosion, ai, sine, foundry,
    crossed_bones, dig, gnaw, mine, dinosaur_bones, wolf, stone_golem, boar, atlas, uluru,
    graveyard, zombie, drown, raise_dead, haunt, spectre, prayer, tumulus, sarcophagus, anubis,
    hurricane, lock, spy,
    sunflower, sun_priest, solar_explosion, solar_power, sun_cloud, eclipse, sun, sunlight,
    solar_system,
    vulture, distraction, bastet, crab, armadillo, crypt, turtle, carrion, maggot,
    duality, sicken, stable,
    bee, beehive, butterfly, spider, mantis, scorpion, honey, beekeep,
    uprising, cornucopia, juggle,
    machine_apocalypse, crowning, nature, desert, privation
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
