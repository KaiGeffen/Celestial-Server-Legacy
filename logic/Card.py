from logic.Effects import Status, Quality
import logic.Catalog

class Card:
    def __init__(self, name, cost=0, points=0, qualities=[], text='', spring=False, dynamic_text=''):
        self.name = name
        self.cost = cost
        self.points = points
        self.qualities = qualities
        self.text = text
        self.spring = spring
        self.dynamic_text = dynamic_text

    # Who is playing, the game model, index of this card in story, auras this round
    # Returns a text recap of playing this card, affects the score as it goes
    def play(self, player, game, index, bonus):
        result = self.points + bonus

        result += game.status[player].count(Status.NOURISH)
        game.status[player] = list(filter(Status.NOURISH.__ne__, game.status[player]))
        result -= game.status[player].count(Status.STARVE)
        game.status[player] = list(filter(Status.STARVE.__ne__, game.status[player]))

        game.score[player] += result

        if result > 0:
            return f"+{result}"
        else:
            return f"{result}"

    def play_spring(self, player, game, index, bonus):
        return self.play(player, game, index, bonus)

    # Get the cost of the card for player in this game state
    def get_cost(self, player, game):
        return self.cost

    # Handle any effects that happen during upkeep
    def on_upkeep(self, player, game):
        pass

    # Handle any effects that happen during the upkeep if this card is in pile
    def pile_upkeep(self, player, game, index):
        return False

    # Handle any effects that happen immediately when the card is player
    def on_play(self, player, game):
        pass

    # Handle anything that happens when flow is triggered by another card in your hand
    def on_flow(self, player, game):
        # False signifies that nothing happened for the flow, cards with effects return true in their overriding methods
        return False

    """GENERIC THINGS A CARD CAN DO"""
    # Reset the scores to 0, 0
    def reset(self, game):
        game.score = [0, 0]
        return '\nReset'

    # Add X mana this turn
    def add_mana(self, amt, game, player):
        game.mana[player] += amt
        for _ in range(amt):
            game.status[player].append(Status.INSPIRED)

    # Add X instances of a given status
    def add_status(self, amt, game, player, stat):
        recap = f'\n{stat.value} {amt}'

        if amt <= 0:
            recap = ''

        for _ in range(amt):
            game.status[player].append(stat)

        return recap

    # Add X mana next turn
    def inspire(self, amt, game, player):
        return self.add_status(amt, game, player, Status.INSPIRE)

    # Next card gives +X points
    def nourish(self, amt, game, player):
        return self.add_status(amt, game, player, Status.NOURISH)

    # Next card gives -X points
    def starve(self, amt, game, player):
        return self.add_status(amt, game, player, Status.STARVE)

    # Your x leftmost cards you can't play next round
    def restrict(self, amt, game, player):
        return self.add_status(amt, game, player, Status.RESTRICT)

    # At start of next turn, create X doves in hand
    def flock(self, amt, game, player):
        return self.add_status(amt, game, player, Status.FLOCK)

    # Draw X cards from deck
    def draw(self, amt, game, player):
        recap = ''

        num_drawn = 0
        for _ in range(amt):
            card = game.draw(player)
            if card:
                num_drawn += 1

        if num_drawn > 0:
            recap = f'\nDraw {num_drawn}'

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
            return f'\nTutor {cost}'

        return ''

    # Discard X cards from hand (left to right). If index specified, discard from that position instead of left-right
    def discard(self, amt, game, player, index=0):
        recap = '\nDiscard:'

        any_seen = False
        for _ in range(amt):
            card = game.discard(player, index=index)
            if card:
                any_seen = True
                recap += f'\n{card.name}'

        if any_seen:
            return recap
        else:
            return ''

    # Remove from the game the lowest X cards from your hand
    def oust(self, amt, game, player):
        recap = '\nOust:'

        any_seen = True
        for _ in range(amt):
            card = game.oust(player)
            if card:
                any_seen = True
                recap += f'\n{card.name}'

        if any_seen:
            return recap
        else:
            return ''

    # Put the top X cards from player's deck on top of their pile
    def mill(self, amt, game, player):
        recap = '\nMill:'

        any_seen = False
        for _ in range(amt):
            card = game.mill(player)
            if card:
                any_seen = True
                recap += f'\n{card.name}'

        if any_seen:
            return recap
        else:
            return ''

    # Oust the top X cards from the player's pile
    def dig(self, amt, game, player):
        recap = '\nRemove:'

        any_seen = False
        for _ in range(amt):
            if game.pile[player]:
                any_seen = True

                card = game.pile[player].pop()
                recap += f'\n{card.name}'

        if any_seen:
            return recap
        else:
            return ''

    # Counter the next act this round for which function returns True
    def counter(self, game, function=None):
        if function is None:
            function = (lambda act: act.countered is False)

        card = game.counter(function)
        if card:
            return f'\nCounter: {card.name}'
        else:
            return ''

    # At the end of this round, if you win, convert points to nourish such that you win by 1
    def gentle(self, game, player):
        recap = '\nGentle'

        game.status[player].append(Status.GENTLE)

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
        for act in game.story.acts:
            if act.owner == player:
                return False
        return True


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

# Card that makes story visible to owner this round
class SightCard(Card):
    def on_play(self, player, game):
        game.vision[player] = True

class FlockCard(Card):
    def __init__(self, name, amt, **args):
        self.amt = amt
        super().__init__(name, **args)

    def play(self, player, game, index, bonus):
        return super().play(player, game, index, bonus) + self.flock(self.amt, game, player)
