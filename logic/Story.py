from enum import Enum

from logic.Recap import Recap


# How an act was added to the story
# Played from hand, sprung from hand, etc
class Source(Enum):
    HAND = 0
    SPRING = 1


class Story:
    def __init__(self):
        self.acts = []
        self.recap = Recap()

    def add_act(self, card, owner, source):
        act = Act(card, owner, source)
        self.acts.append(act)

    def run(self, game):
        # Reset the recap so that it now recaps this run
        self.recap.reset()

        # TODO remove index and bonus from play signature
        index = 0
        # TODO use source
        for act in self.acts:
            result = act.card.play(player=act.owner,
                                 game=game,
                                 index=index,
                                 bonus=0)

            self.recap.add(act.card, act.owner, result)

    def clear(self):
        self.acts = []


class Act:
    def __init__(self, card, owner, source):
        self.card = card
        self.owner = owner
        self.source = source
