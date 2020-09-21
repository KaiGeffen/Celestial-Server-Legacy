from logic.Effects import *
import logic.Catalog

class Card:
    def __init__(self, name, cost=0, points=0, qualities=[], auras=[], supports=[], traumas=[], goals=[], text='', spring=None, dynamic_text=''):
        self.name = name
        self.cost = cost
        self.points = points
        self.qualities = qualities
        self.auras = auras
        self.supports = supports
        self.traumas = traumas
        self.goals = goals
        self.text = text
        self.spring = spring
        self.dynamic_text = dynamic_text

    # Who is playing, the game model, index of this card on stack, auras this round
    # Returns a text recap of playing this card, affects the score as it goes
    def play(self, player, game, index, bonus):
        result = self.points + bonus

        result += game.status[player].count(Support.NOURISH)
        game.status[player] = list(filter((Support.NOURISH).__ne__, game.status[player]))
        result -= game.status[player].count(Support.STARVE)
        game.status[player] = list(filter((Support.STARVE).__ne__, game.status[player]))

        game.score[player] += result

        if result > 0:
            return f"+{result}"
        else:
            return f"{result}"

    # Get the cost of the card for player in this game state
    def get_cost(self, player, game):
        return self.cost

    # Handle any effects that happen during upkeep
    def on_upkeep(self, player, game):
        pass

    # Handle any effects that happen immediately when the card is player
    def on_play(self, player, game):
        pass

    # Everything that happens when flow is triggered by another card in your hand
    def on_flow(self, player, game):
        return False

    """GENERIC THINGS A CARD CAN DO"""
    # Reset the scores to 0, 0
    def reset(self, game):
        game.score = [0, 0]
        return '\nReset'

    # Add x mana next turn
    def inspire(self, amt, game, player):
        recap = '\nInspire'
        if amt > 1:
            recap += f' {amt}'

        for _ in range(amt):
            game.status[player].append(Support.BOOST)

        return recap

    # Next card +x points
    def nourish(self, amt, game, player):
        recap = '\nNourish'
        if amt > 1:
            recap += f' {amt}'

        for _ in range(amt):
            game.status[player].append(Support.NOURISH)

        return recap

    # Next card -x points
    def starve(self, amt, game, player):
        recap = '\nStarve'
        if amt > 1:
            recap += f' -{amt}'

        for _ in range(amt):
            game.status[player].append(Support.STARVE)

        return recap

    # Draw x cards from deck
    def draw(self, amt, game, player):
        recap = ''

        for _ in range(amt):
            card = game.draw(player)
            if card:
                recap += f'\nDraw: {card.name}'

        return recap

    # Create in hand a copy of the given card
    def create(self, card, game, player):
        if game.create(player, card):
            return f'\nCreate: {card.name}'
        else:
            return ''

    # Tutor a card with cost x
    def tutor(self, cost, game, player):
        card = game.tutor(player, cost)
        if card:
            return f'\nTutor: {card.name}'

        return ''

    # Discard x cards from hand (left to right). If index specified, discard from that position instead of left-right
    def discard(self, amt, game, player, index=0):
        recap = ''

        for _ in range(amt):
            card = game.discard(player, index=index)
            if card:
                recap += f'\nDiscard: {card.name}'

        return recap

    # Banish the lowest X cards from your hand
    def oust(self, amt, game, player):
        recap = ''

        for _ in range(amt):
            card = game.oust(player)
            if card:
                recap += f'\nOust: {card.name}'

        return recap

    # Counter the next card on the stack
    def counter(self, game):
        card = game.counter()
        if card:
            return f'\nCounter: {card.name}'
        else:
            return ''

    # At start of next turn, create x doves
    def flock(self, amt, game, player):
        recap = '\nFlock'

        if amt > 1:
            recap += f' {amt}'

        for _ in range(amt):
            game.status[player].append(Support.FLOCK)

        return recap

    # At the end of this round, if you win, convert points to nourish such that you win by 1
    def gentle(self, game, player):
        recap = '\nGentle'

        game.status[player].append(Support.GENTLE)

        return recap

    # If no robot is in hand, make a 0:X fleeting robot, otherwise add +X to the existing robot
    def build(self, amt, game, player):
        # TODO Method for checking something is in hand
        for card in game.hand[player]:
            if card.name == 'Robot':
                card.points += amt
                card.dynamic_text = f'0:{card.points}, fleeting'
                return f'\nBuild +{amt}'

        card = Card(name='Robot', points=amt, qualities=[Quality.FLEETING], dynamic_text=f'0:{amt}, fleeting')
        if game.create(player, card):
            return f'\nBuild {amt}'
        else:
            return ''




    """UTILITY CHECKS"""
    def your_final(self, game, player):
        for (card, owner) in game.stack:
            if owner == player:
                return False
        return True

    def get_points(self, bonus, stack, auras, index, player):
        result = self.points + bonus

        if Quality.LAUNCH in self.qualities:
            if index == 0:
                result += 2

        if Quality.FINALE in self.qualities:
            if len(stack) == 0:
                result += 2

        if Quality.TRIBUTE in self.qualities:
            result += index

        if Quality.SMASH in self.qualities:
            if len(stack) > 0:
                next_card_on_stack = stack[0][0]
                if next_card_on_stack.cost >= 2:
                    result += 2

        # PLUMMET
        result -= auras.count(Aura.PLUMMET)

        # Spike reduces points to 0 after everything
        if Aura.SPIKE in auras:
            result = 0

        return result
        # return max(0, result)

    def get_auras(self, stack, player):
        return self.auras

    # Return 2 bools for if each player met the goal and should be awarded a heart
    # If self isn't a goal card, return False for both
    def get_goal_result(self, stack):

        # Pointless Machines : Player who plays the most cards more than 3
        if Goal.POINTLESS_MACHINES in self.goals:

            MINIMUM = 3
            card_count = [0, 0]
            for (card, owner) in stack:
                if owner == 0:
                    card_count[0] += 1
                else:
                    card_count[1] += 1

            if card_count[0] >= MINIMUM and card_count[0] > card_count[1]:
                return [True, False]
            elif card_count[1] >= MINIMUM and card_count[1] > card_count[0]:
                return [False, True]
            elif card_count[0] >= MINIMUM and card_count[0] == card_count[1]:
                return [True, True]
            else:
                return [False, False]

        # Resurrections : Player who played highest cost card, costing at least 5
        if Goal.RESURRECTIONS in self.goals:
            MINIMUM = 5
            high_score = [0, 0]
            for (card, owner) in stack:
                # TODO Current implementation means that any 5 ties with Mirror (Even if it would become higher)
                high_score[owner] = max(card.cost, high_score[owner])

            if high_score[0] >= MINIMUM and high_score[0] > high_score[1]:
                return [True, False]
            elif high_score[1] >= MINIMUM and high_score[1] > high_score[0]:
                return [False, True]
            elif high_score[0] >= MINIMUM and high_score[0] == high_score[1]:
                return [True, True]
            else:
                return [False, False]

        # Self is not a goal
        return [False, False]


class FireCard(Card):
    def play(self, player, game, index, bonus):
        bonus = bonus - index
        return super().play(player, game, index, bonus)

# Trigger the leftmost flow card when this is played
class EbbCard(Card):
    def on_play(self, player, game):
        for card in game.hand[player]:
            if card.on_flow(player, game):
                return

# When ebb is activated, cycle me from hand
class FlowCard(Card):
    def on_flow(self, player, game):
        game.cycle(player, self)
        return True

# Card that makes stack visible to owner this round
class SightCard(Card):
    def on_play(self, player, game):
        game.vision[player] = True

class FlockCard(Card):
    def __init__(self, name, amt, **args):
        self.amt = amt
        super().__init__(name, **args)

    def play(self, player, game, index, bonus):
        recap = '\nFlock'
        if self.amt > 1:
            recap += f' x{self.amt}'

        for _ in range(self.amt):
            game.status[player].append(Support.FLOCK)

        return super().play(player, game, index, bonus) + recap
