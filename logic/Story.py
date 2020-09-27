from enum import Enum

from logic.Recap import Recap
from logic.Effects import Quality

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
        while self.acts:
            act = self.acts.pop(0)

            if act.countered:
                result = 'Countered'
            else:
                if act.source is Source.HAND:
                    result = act.card.play(player=act.owner,
                                           game=game,
                                           index=index,
                                           bonus=0)
                elif act.source is Source.SPRING:
                    result = act.card.play_spring(player=act.owner,
                                           game=game,
                                           index=index,
                                           bonus=0)

            if Quality.FLEETING not in act.card.qualities:
                game.pile[act.owner].append(act.card)

            index += 1

            self.recap.add(act.card, act.owner, result)

    def clear(self):
        self.acts = []

    def get_length(self):
        return len(self.acts)

    def counter(self, index):
        if self.get_length() > index:
            self.acts[index].countered = True

            return self.acts[index].card
        else:
            return None

    def move_act(self, index_origin, index_dest):
        act = self.acts.pop(index_origin)
        self.acts.insert(index_dest, act)

        return act


class Act:
    def __init__(self, card, owner, source):
        self.card = card
        self.owner = owner
        self.source = source
        self.countered = False
