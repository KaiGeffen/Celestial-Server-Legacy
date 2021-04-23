from logic.ServerController import ServerController
from logic.ServerModel import ServerModel
from logic.Catalog import *


class TutorialController(ServerController):
    def __init__(self):
        # NOTE The last cards are the top of the deck, which isn't shuffled for tutorial
        player_deck = [dash, dove, dove, dove, gift, dash, dash, dash,
                    dove, dove, dash, dove, dash, dove, dove]
        ai_deck = [drown, paranoia,
                   paranoia, drown, drown, drown, drown, drown, drown]
        self.model = ServerModel(player_deck, ai_deck, shuffle=False)

    # Ensure that player has priority
    def start(self):
        super().start()
        self.model.priority = 0

    # TODO Don't copy so much, call something
    # Perform the takedown phase
    def do_takedown(self):

        # Resolve the story
        self.model.score = [0, 0]
        wins = [0, 0]

        # Reset to a new Recap for this round's takedown
        self.model.recap.reset()

        self.model.story.run(self.model, isSimplified=True)

        # Add to wins here
        if self.model.score[0] > self.model.score[1] + self.model.status[1].count(Status.SAFE):
            if self.model.score[0] > 0:
                wins[0] += 1
        elif self.model.score[1] > self.model.score[0] + self.model.status[0].count(Status.SAFE):
            if self.model.score[1] > 0:
                wins[1] += 1
        else:
            pass
        # Adjust the scores to reflect the wins from this round
        self.model.wins[0] += wins[0]
        self.model.wins[1] += wins[1]

        # Recap the results
        safe_totals = [self.model.status[0].count(Status.SAFE),
                       self.model.status[1].count(Status.SAFE)]
        self.model.recap.add_total(self.model.score, wins, safe_totals)

        # Remember how the round ended for user's recap (Must come after wins are determined)
        self.model.story.save_end_state(self.model)
        self.model.story.clear()
