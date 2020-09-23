from enum import Enum


class Quality(Enum):
    FLEETING = "Fleeting"
    VISIBLE = "Visible"


class Status(Enum):
    FLOCK = "Flock"
    BOOST = "Boost"
    NOURISH = "Nourish"
    STARVE = "Starve"
    GENTLE = "Gentle"
    RESTRICT = "Restrict"
    RESTRICTED = "Restricted"
