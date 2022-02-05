# Play = 'play'
# Pass = 'pass'
Draw = 'draw'
Discard = 'discard'
TutorDeck = 'tutor_deck'
TutorDiscard = 'tutor_discard'
Create = 'create'
Shuffle = 'shuffle'
Mill = 'mill'
Top = 'top'


class Animation(dict):
    def __init__(self, zone_from, zone_to=None, card=None, index=None):
        dict.__init__(self,
                      zone_from=zone_from,
                      zone_to=zone_to,
                      card=card,
                      index=index)

# Resolve = 'resolve'
# Win = 'win'
# Lose = 'lose'
# Tie = 'tie'
#
# Build = 'build'
# Inspire = 'inspire'
# Nourish = 'nourish'
#
# Meow = 'meow'
# Yell = 'yell'
# BoneSnap = 'bone_snap'
# Bird = 'bird'
# Drown = 'drown'
# Fire = 'fire'
# Reset = 'reset'
# Crowd = 'crowd'
# Sarcophagus = 'sarcophagus'
