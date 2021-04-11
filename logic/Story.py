from enum import Enum

import SoundEffect
from logic.Recap import Recap
from logic.Effects import Quality


# How an act was added to the story
# Played from hand, sprung from hand, etc
class Source(Enum):
    HAND = 0
    SPRING = 1
    PILE = 2


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

        state_before_play = ['', '']
        for player in [0, 1]:
            state_before_play[player] = game.get_client_model(player=player, total_vision=True)
        self.recap.add_state(state_before_play)

        index = 0
        while self.acts:
            act = self.acts.pop(0)

            game.sound_effect = SoundEffect.Resolve

            if act.countered:
                result = 'Countered'
            else:
                if act.source is Source.HAND or act.source is Source.PILE:
                    result = act.card.play(player=act.owner,
                                           game=game,
                                           index=index,
                                           bonus=act.bonus)
                elif act.source is Source.SPRING:
                    result = act.card.play_spring(player=act.owner,
                                                  game=game,
                                                  index=index,
                                                  bonus=act.bonus)

            # Card goes to pile unless it has fleeting
            if Quality.FLEETING not in act.card.qualities:
                game.pile[act.owner].append(act.card)

            index += 1

            self.recap.add(act.card, act.owner, result)

            # Save as a string what state the game is in after the card has been played
            state_after_play = ['', '']
            for player in [0, 1]:
                state_after_play[player] = game.get_client_model(player=player, total_vision=True)

            self.recap.add_state(state_after_play)

    def save_end_state(self, game):
        # Save an ending state which includes win/loss/tie sfx
        state_after_play = ['', '']
        for player in [0, 1]:
            # Win/Lose based on which player the state is for
            if self.recap.wins[player] > 0:
                game.sound_effect = SoundEffect.Win
            elif self.recap.wins[player ^ 1] > 0:
                game.sound_effect = SoundEffect.Lose
            else:
                game.sound_effect = SoundEffect.Tie

            state_after_play[player] = game.get_client_model(player=player, total_vision=True)
        self.recap.add_state(state_after_play)

    def clear(self):
        self.acts = []

    def get_length(self):
        return len(self.acts)

    def is_empty(self):
        return len(self.acts) == 0

    def counter(self, function):
        for act in self.acts:
            if function(act):
                act.countered = True

                return act.card

        return None
        # if self.get_length() > index:
        #     self.acts[index].countered = True
        #
        #     return self.acts[index].card
        # else:
        #     return None

    # TODO This has a bug if origin is before destination, since the indexing changes in that case
    def move_act(self, index_origin, index_dest):
        act = self.acts.pop(index_origin)
        self.acts.insert(index_dest, act)

        return act

    # Replace the act at index with replacement_act
    def replace_act(self, index, replacement_act):
        if len(self.acts) < index + 1:
            raise Exception(f"Tried to replace act {index} in a story with only {len(self.acts)} acts.")

        self.acts[index] = replacement_act


class Act:
    def __init__(self, card, owner, source):
        self.card = card
        self.owner = owner
        self.source = source

        self.countered = False
        self.bonus = 0
