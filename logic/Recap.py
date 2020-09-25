# A recap of what happened last round, including the cards played by whom and what they did, textually
class Recap:
    def __init__(self, story=[], sums=[0, 0], wins=[0, 0]):
        self.story = story
        self.sums = sums
        self.wins = wins

    # In most cases, text is +N, but for things like RESET it could be different
    def add(self, card, owner, text):
        self.story.append((card, owner, text))

    def add_total(self, sums, wins):
        self.sums[0] += sums[0]
        self.sums[1] += sums[1]

        self.wins[0] += wins[0]
        self.wins[1] += wins[1]

    def reset(self):
        self.story = []
        self.sums = [0, 0]
        self.wins = [0, 0]

    # Return a flipped version of this recap
    def get_flipped(self):
        story = []
        for (card, owner, text) in self.story:
            story.append((card, (owner + 1) % 2, text))

        sums = self.sums[::-1]
        wins = self.wins[::-1]

        return Recap(story, sums, wins)
