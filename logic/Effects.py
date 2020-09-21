from enum import Enum


class Quality(Enum):
    FLEETING = "Fleeting"
    TRIBUTE = "Tribute"
    FINALE = "Finale"
    LAUNCH = "Launch"
    SMASH = "Smash"
    RESET = "Reset"
    CLEANSE = "Cleanse"
    VISIBLE = "Visible"
    MIRROR = "Mirror"
    FORTRESS = "Fortress"
    FUEL = "Fuel"


# SPIKES - The next card played this round is counter; it gives 0 points, no effects, no goals
class Aura(Enum):
    SPIKE = "Spike"
    PLUMMET = "Plummet"


class Support(Enum):
    FLOCK = "Flock"
    BOOST = "Boost"
    NOURISH = "Nourish"
    STARVE = "Starve"
    CELERITY = "Celerity"
    WONDER = "Wonder"
    RELEASE = "Release"
    GENTLE = "Gentle"


class Trauma(Enum):
    LOSS = "Loss"

#
# class Burst(Enum):
#     VISION = "Vision"
#     LOCK = "Lock"


class Goal(Enum):
    POINTLESS_MACHINES = 1
    RESURRECTIONS = 2
