# A recap of what happened last round, including the cards played by whom and what they did, textually
class Recap:
    def __init__(self, story=[], sums=[0, 0], wins=[0, 0], safety=[0, 0], state_list=[]):
        self.story = story
        self.sums = sums
        self.wins = wins
        self.safety = safety

        # List of what each player sees as the game-state after each act in the story
        # The state is a dictionary representation of client's view, starting before the first act resolves
        # [[state_p0_0, state_p1_0], [state_p0_1, state_p1_1], etc]
        self.state_list = state_list

    # In most cases, text is +N, but for things like RESET it could be different
    def add(self, card, owner, text):
        self.story.append((card, owner, text))

    # Add the state of the game each player sees to the ongoing list
    def add_state(self, state_pair):
        self.state_list.append(state_pair)

    def add_total(self, sums, wins, safety):
        self.sums[0] += sums[0]
        self.sums[1] += sums[1]

        self.wins[0] += wins[0]
        self.wins[1] += wins[1]

        self.safety[0] += safety[0]
        self.safety[1] += safety[1]

    def reset(self):
        self.story = []
        self.sums = [0, 0]
        self.wins = [0, 0]
        self.safety = [0, 0]
        self.state_list = []

    # Return a flipped version of this recap
    def get_flipped(self):
        story = []
        for (card, owner, text) in self.story:
            story.append((card, (owner + 1) % 2, text))

        sums = self.sums[::-1]
        wins = self.wins[::-1]
        safety = self.safety[::-1]
        state_list = [relative_states[::-1] for relative_states in self.state_list]

        return Recap(story, sums, wins, safety, state_list)

    # Return as a list of strings the states the given player sees
    def get_state_list(self, player):
        return [relative_states[player] for relative_states in self.state_list]
