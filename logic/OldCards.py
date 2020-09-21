from logic.Card import Card
from logic.Effects import *

# Vanilla cards
badeline = Card(name="Badeline", cost=1, points=1, text="1 for 1")
oshiro = Card(name="Oshiro", cost=2, points=2, text="2 for 2")
crow = Card(name="Crow", cost=3, points=3, text="3 for 3")
theo = Card(name="Theo", cost=4, points=4, text="4 for 4")
madeline = Card(name="Madeline", cost=5, points=5, text="5 for 5")
granny = Card(name="Granny", cost=6, points=6, text="6 for 6")


# Bonus
disappearing_platform = Card(name="Disappearing Platform", cost=1, points=0, qualities=[Quality.FINALE], text="0 for 1, or 2 for 1 as final card")
spring = Card(name="Spring", cost=2, points=1, qualities=[Quality.LAUNCH], text="1 for 2, or 3 for 2 as first card")
smashable_wall = Card(name="Smashable Wall", cost=3, points=2, qualities=[Quality.SMASH], text="2 for 3, or 4 if the next card costs 2+")
falling_platform = Card(name="Falling Platform", cost=4, points=3, qualities=[Quality.FINALE], text="3 for 4, or 5 for 4 as final card")
conveyor_belt_platform = Card(name="Conveyor-Belt Platform", cost=5, points=4, qualities=[Quality.LAUNCH], text="4 for 5, or 6 for 5 as first card")
memorial = Card(name="Memorial", cost=6, points=3, qualities=[Quality.TRIBUTE], text="3 for 6, +1 for the max of cards before/cards after")


# Carryover
diamond = Card(name="Diamond", cost=0, supports=[Support.BOOST], text="0: +1 mana next turn")
strawberry = Card(name="Strawberry", cost=3, supports=[Support.NOURISH, Support.NOURISH], text="3: Your next card has +2")
alternating_platform = Card(name="Alternating Platforms", cost=2, points=4, supports=[Support.STARVE, Support.STARVE, Support.STARVE], text="4 for 2: Your next card -3")

birds = Card(name="Birds", cost=1, points=1, qualities=[Quality.FLEETING, Quality.VISIBLE], text="1 for 1, exiled instead of shuffled")
nest = Card(name="Nest", cost=2, points=1, supports=[Support.FLOCK, Support.FLOCK, Support.FLOCK], text="1 for 2, draw 3 birds next turn")
brood = Card(name="Brood", cost=5, points=5, qualities=[Quality.VISIBLE], supports=[Support.FLOCK], text="5 for 5, draw a bird next turn")

class BlueCrow(Card):
    def get_points(self, bonus, stack, auras, index, player):
        bird_count = 0
        for card, owner in stack:
            if card is birds and owner is player:
                bird_count += 1
        return bird_count + super().get_points(bonus, stack, auras, index, player)
blue_crow = BlueCrow(name="Blue Crow", cost=3, points=2, text="2 + X for 3, X is birds you play after this")
class Dove(Card):
    # TODO This is a weird place to put the card having an effect, figure out how
    # stack resolving works
    def get_points(self, bonus, stack, auras, index, player):
        # Your later birds have reset
        for card, owner in stack:
            if card is birds and owner is player:
                card.qualities.append(Quality.RESET)
                card.score = 0

        return super().get_points(bonus, stack, auras, index, player)
dove = Dove(name="Dove", cost=4, text="4: Your later birds have reset and 0 points")

# Control
spikes = Card(name="Spikes", cost=2, points=1, auras=[Aura.SPIKE], text="1 for 2: Counter the next card")
checkpoint = Card(name="Checkpoint", cost=4, qualities=[Quality.RESET], text="4: Reset the scores this round")
collapsing_bridge = Card(name="Collapsing Bridge", cost=4, points=3, auras=[Aura.PLUMMET], text="3 for 4. Cards this round are worth 1 point less")


# Hearts
pointless_machines = Card(name="Pointless Machines", qualities=[Quality.VISIBLE], goals=[Goal.POINTLESS_MACHINES], text="Goal: Play 3 cards")


"""CHAPTER 2"""
binoculars = Card(name="Binoculars", cost=0, bursts=[Burst.VISION], text="This round, you can see all cards on the stack")
seed = Card(name="Seed", cost=1, supports=[Support.NOURISH], text="1: Next card gives +1")
mirror = Card(name="Mirror", cost=6, qualities=[Quality.MIRROR], text="Needs work feels cheat")
fortress = Card(name="Fortress", cost=4, points=4, qualities=[Quality.FORTRESS], text="4/4: Cancel all wins up to this point, if you do, -4")
star_block = Card(name="Star Block", cost=2, supports=[Support.CELERITY], text="2, each card this round has Boost")

dreamer = Card(name="Dreamer", cost=6, points=1, qualities=[Quality.RESET], text="1 for 6, reset the scores this round")
mother = Card(name="Mother", cost=7, points=8, text="8 for 7")
nightmare = Card(name="Nightmare", cost=8, points=5, traumas=[Trauma.LOSS, Trauma.LOSS], text="5 for 8, opponent discards 2")

resurrections = Card(name="Resurrections", qualities=[Quality.VISIBLE], goals=[Goal.RESURRECTIONS], text="Goal: Play the highest cost card")

"""Chapter 3"""
# sludge = Card(name="Sludge", cost=1, qualities=[Quality.LOSS], text="Give your opponent a sludge")
vulture = Card(name="Vulture", cost=3, points=3, supports=[Support.RELEASE, Support.FLOCK], text="3 for 3, flock. Oust lowest card in hand.")


"""SNAKES"""
dragon_skull_spring = Card(name="Dragon Skull", qualities=[Quality.FLEETING], text="spring, discarded, ousted: +1 mana")
dragon_skull = Card(name="Dragon Skull", qualities=[Quality.FUEL], text="spring, discarded, ousted: +1 mana", spring=dragon_skull_spring)

snake_egg_spring = Card(name="Snake Egg", points=1, qualities=[Quality.FLEETING], text="1 for 1, spring: 1 point")
snake_egg = Card(name="Snake Egg", cost=1, points=1, text="1 for 1, spring: 1 point", spring=snake_egg_spring)

ouroboros_spring = Card(name="Ouroboros", qualities=[Quality.FLEETING], supports=[Support.RELEASE, Support.RELEASE, Support.RELEASE, Support.WONDER, Support.WONDER, Support.WONDER], text="2 for 2, spring: ours 3 draw 3")
ouroboros = Card(name="Ouroboros", cost=2, points=2, text="2 for 2, spring: oust 3 draw 3", spring=ouroboros_spring)

serpent_spring = Card(name="Serpent", qualities=[Quality.FLEETING], traumas=[Trauma.LOSS], text="3 for 3, spring: opponent discards 1")
serpent = Card(name="Serpent", cost=3, points=3, text="3 for 3, spring: opponent discards 1", spring=serpent_spring)

temptation_spring = Card(name="Temptation", qualities=[Quality.FLEETING, Quality.CLEANSE], text="3 for 4, spring or play: remove all statuses from both players")
temptation = Card(name="Temptation", cost=3, points=4, qualities=[Quality.CLEANSE], text="3 for 4, spring or play: remove all statuses from both players", spring=temptation_spring)

sand_snake_spring = Card(name="Sand Snake", qualities=[Quality.FLEETING], supports=[Support.WONDER], text="5 for 5, spring: draw 1")
sand_snake = Card(name="Sand Snake", cost=5, points=5, text="5 for 5, spring: draw 1", spring=sand_snake_spring)

dragon_spring = Card(name="Dragon", qualities=[Quality.FLEETING], text="7 for 6, visible, spring")
dragon = Card(name="Dragon", cost=6, points=7, qualities=[Quality.VISIBLE], text="7 for 6, visible, spring", spring=dragon_spring)


# List of all cards currently usable in game
old_cards = [badeline, oshiro, crow, theo, madeline, granny, mother, nightmare,
             disappearing_platform, spring, smashable_wall, falling_platform, conveyor_belt_platform, memorial,
             seed, strawberry,
             birds, nest, blue_crow, vulture, dove, brood, diamond, star_block,
             dragon_skull, snake_egg, ouroboros, serpent, temptation, sand_snake, dragon,
             binoculars, alternating_platform, checkpoint, fortress, collapsing_bridge,
             pointless_machines, resurrections,
             ]
