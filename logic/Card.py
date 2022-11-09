import CardCodec
from logic.Effects import Status, Quality
import SoundEffect
from logic.Story import Act
from Animation import Animation


class Card:
    def __init__(self, name, cost=0, points=0, qualities=[], text='', spring=False, pile_highlight=False, dynamic_text='', id=-1, rarity=None):
        self.name = name
        self.cost = cost
        self.points = points
        self.qualities = qualities
        self.text = text
        self.spring = spring
        self.pile_highlight = pile_highlight
        self.dynamic_text = dynamic_text
        self.id = id
        self.rarity = rarity

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

    # Rate the heuristic value of playing this card in the given world-model
    def rate_play(self, world):
        # Default is to just value it as its cost
        return max(1, self.cost)

    # Rate how much this card wants to be played later in the story as opposed to early
    def rate_delay(self, world):
        return 0

    # Get the cost of the card for player in this game state
    def get_cost(self, player, game):
        return self.cost

    # Handle any effects that happen during upkeep
    def on_upkeep(self, player, game, index):
        return False

    # Handle any effects that trigger when you play a card while this is in your hand
    def in_hand_on_play(self, player, game):
        return False

    # Handle any effects that happen during the upkeep if this card is in pile
    def morning(self, player, game, index):
        return False

    # Handle any effects that happen immediately when the card is player
    def on_play(self, player, game):
        pass

    """GENERIC THINGS A CARD CAN DO"""
    # Reset the scores to 0, 0 - removes all safe
    def reset(self, game):
        game.score = [0, 0]

        game.sound_effect = SoundEffect.Reset

        return '\nReset'

    # Add X mana this turn
    def add_mana(self, amt, game, player):
        game.mana[player] += amt
        for _ in range(amt):
            game.status[player].append(Status.INSPIRED)

        if amt > 0:
            return f'\n+{amt} mana'
        else:
            return ''

    # Add X instances of a given status
    def add_status(self, amt, game, player, stat):
        recap = f'\n{stat.value} {amt}'

        if amt <= 0:
            recap = ''

        for _ in range(amt):
            game.status[player].append(stat)

        return recap

    # Remove all instances of the given status
    def remove_status(self, game, player, removed_status):
        def clear_status(stat):
            return stat is not removed_status
        game.status[player] = list(filter(clear_status, game.status[player]))

    # Add X mana next turn
    def inspire(self, amt, game, player):
        game.animations[player].append(
            Animation('Status', index=0))

        game.sound_effect = SoundEffect.Inspire

        return self.add_status(amt, game, player, Status.INSPIRE)

    # Next card gives +X points
    def nourish(self, amt, game, player):
        game.animations[player].append(
            Animation('Status', index=2))

        game.sound_effect = SoundEffect.Nourish

        return self.add_status(amt, game, player, Status.NOURISH)

    # Next card gives -X points
    def starve(self, amt, game, player):
        game.animations[player].append(
            Animation('Status', index=3))
        return self.add_status(amt, game, player, Status.STARVE)

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
        return game.create(player, card)

    # Create in pile a copy of the given card
    def create_in_pile(self, card, game, player):
        game.create_in_pile(player, card)

        return f'\n{card.name}'

    # Create at the end of the story a copy of the given card
    def create_in_story(self, card, game, player):
        game.create_in_story(player, card)

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

    # Put X cards from hand on the bottom of deck (left to right).
    def bottom(self, amt, game, player):
        recap = '\nBottom'

        any_seen = False
        for _ in range(amt):
            card = game.bottom(player)
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

        any_seen = False
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
        game.dig(player, amt)

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
                card.dynamic_text = f'0:{card.points}, Fleeting'

                game.sound_effect = SoundEffect.Birth
                return f'\nBuild +{amt}'

        card = Card(name='Robot', points=amt, qualities=[Quality.FLEETING], dynamic_text=f'0:{amt}, fleeting', id=1003)
        if game.create(player, card):
            game.sound_effect = SoundEffect.Birth
            return f'\nBuild {amt}'
        else:
            return ''

    # Transform the card in the story at index into the given card
    def transform(self, index, card, game):
        if index + 1 <= len(game.story.acts):
            act = game.story.acts[index]
            old_card = act.card
            game.story.replace_act(index, Act(
                card=card,
                owner=act.owner
            ))

            # Add an animation
            game.animations[act.owner].append(
                Animation('Transform', 'Story', CardCodec.encode_card(old_card), index=index))

    # Remove and return the act at given index (Must be valid)
    def remove_act(self, index, game):
        result = game.remove_act(index)
        return result

    """UTILITY CHECKS"""
    def your_final(self, game, player):
        for act in game.story.acts:
            if act.owner == player:
                return False
        return True

    # Rate how valuable resetting is in the given world
    def rate_reset(self, world):
        # Approximate the known value of cards in the story
        known_value = 0
        their_unknown_cards = 0
        their_mana = world.max_mana[1] + world.opp_status.count(Status.INSPIRED)

        for act in world.story.acts:
            card = act.card

            if act.owner == 0:
                known_value -= card.cost
            elif Quality.VISIBLE in card.qualities:
                known_value += card.cost
                their_mana -= card.cost
            else:
                their_unknown_cards += 1

        # Guess the cost of the unknown cards they have played as half of remaining mana
        value = known_value
        for i in range(their_unknown_cards):
            guessed_value = their_mana // 2

            value += guessed_value
            their_mana -= guessed_value

        return value

    # Rate how valuable forcing the opponent to discard a card is
    def rate_discard(self, world):
        # Extra cards achieved by previous acts
        extra_cards = 0
        for act in world.story.acts:
            if act.card.name == 'Gift' or act.card.name == 'Mercy':
                extra_cards += 1
            elif act.card.name == 'Dagger' or act.card.name == 'Bone Knife' or act.card.name == 'Chimney':
                extra_cards -= 1

        cards_in_hand_to_value = [
            0,
            0.6,
            0.8,
            1,
            1,
            0.2,
            0.1
        ]

        hand_count = max(0, min(6, world.opp_hand + extra_cards))

        return cards_in_hand_to_value[hand_count]


class FireCard(Card):
    def play(self, player, game, index, bonus):
        # game.sound_effect = SoundEffect.Fire
        bonus = bonus - index
        return super().play(player, game, index, bonus)

    def rate_play(self, world):
        return self.points - len(world.story.acts)

# Card that makes story visible to owner this round
class SightCard(Card):
    def __init__(self, amt, **kwargs):
        self.amt = amt
        super().__init__(**kwargs)

    def on_play(self, player, game):
        game.vision[player] += self.amt
