import copy
import json

from logic.Catalog import all_cards
from logic.Recap import Recap
from logic.Effects import Status
from logic.Story import Story, Source

# DELIM1 separates the elements of the largest data structure (ex: Recap)
# DELIM2 separates the individual entries of the lower level data struct (ex: List of cards)
DELIM1 = '¡'
DELIM2 = '™'
DELIM_DYN_TEXT = '£'
# For when the recap sends full state before/after each act
DELIM_FULL_STATE = 'ª'


# Encode / Decode methods for sending the decklist to server
def encode_card(card):
    for catalog_entry in all_cards:
        if card.name == catalog_entry.name:
            if card.dynamic_text:
                return str(card.id) + DELIM_DYN_TEXT + card.dynamic_text
            else:
                return str(card.id)
    print(f"Encoding error for card {card}")
    raise Exception('Card encoding broken')

def encode_deck(deck):
    return DELIM2.join(list(map(encode_card, deck)))

def decode_card(s):
    sections = s.split(DELIM_DYN_TEXT)

    card_id = int(sections[0])
    dynamic_text = sections[1] if len(sections) > 1 else None

    card = None
    for c in all_cards:
        if card_id == c.id:
            card = c
            break

    if dynamic_text:
        card = copy.deepcopy(card)
        card.text = dynamic_text

    return card

def decode_deck(deck_codes):
    if deck_codes:
        if DELIM2 in deck_codes:
            cards = deck_codes.split(DELIM2)
        else:
            cards = deck_codes.split(':')
        return list(map(decode_card, cards))
    else:
        return []


def encode_story(stack):
    def encode_act(play):
        card_id, owner = play
        return f'{encode_card(card_id)}{DELIM2}{owner}'

    result = DELIM1.join(list(map(encode_act, stack)))
    return result


def decode_story(s):
    # If the story is empty, return empty list
    story = Story()
    if not s:
        return story

    for act in s.split(DELIM1):
        l = act.split(DELIM2)

        card = decode_card(l[0])
        owner = int(l[1])

        # TODO If source ever matters (to client), send and decode that as well
        story.add_act(card, owner, Source.HAND)

    return story


# If shallow, don't encode earlier states just remember the cards/outcomes
def encode_recap(recap, shallow):
    result = f'{recap.sums[0]}{DELIM2}{recap.sums[1]}{DELIM1}' \
             f'{recap.wins[0]}{DELIM2}{recap.wins[1]}{DELIM1}' \
             f'{recap.safety[0]}{DELIM2}{recap.safety[1]}'

    # If there is a story, add that
    if recap.story:
        result += DELIM1

        # Encode a single play of the recap, including textual description of what happened
        def encode_play(play):
            card, owner, text = play
            return f'{encode_card(card)}{DELIM2}{owner}{DELIM2}{text}'

        result += DELIM1.join(list(map(encode_play, recap.story)))

    # If a state list exists, add that (List of states visited in the recap)
    # Add the full list of states that this player sees before/after each act in story
    if recap.state_list and not shallow:
        result += DELIM_FULL_STATE
        result += DELIM_FULL_STATE.join(
            list(map(json.dumps, recap.get_state_list(player=0))))

    return result


def decode_recap(s):
    # NOTE Full_state part is not supported in python version
    s = s.split(DELIM_FULL_STATE)[0]

    recap = s.split(DELIM1, maxsplit=3)
    sums = list(map(int, recap[0].split(DELIM2)))
    wins = list(map(int, recap[1].split(DELIM2)))
    safety = list(map(int, recap[2].split(DELIM2)))

    # If no plays happened, just return sums, wins, and safety recap
    if len(recap) == 3:
        return Recap(sums=sums, wins=wins, safety=safety)

    plays = recap[3].split(DELIM1)

    def decode_play(play: str):
        l = play.split(DELIM2)

        card = decode_card(l[0])
        owner = int(l[1])
        text = l[2]

        return card, owner, text

    story = list(map(decode_play, plays))
    return Recap(story=story, sums=sums, wins=wins, safety=safety)


def encode_statuses(statuses):
    def encode_status(status): return status.value
    return DELIM1.join(list(map(encode_status, statuses)))


def decode_statuses(s):
    if not s:
        return []

    def decode_status(stat: str): return Status(stat)
    return list(map(decode_status, s.split(DELIM1)))


def encode_mulligans(mulligans):
    result = ''
    for mulligan in mulligans:
        if mulligan:
            result += '1'
        else:
            result += '0'

    return result

def decode_mulligans(s):
    mulligans = []
    for c in s:
        if c == '1':
            mulligans.append(True)
        elif c == '0':
            mulligans.append(False)
        else:
            raise Exception(f'Invalid mulligans: {s}')

    return mulligans
