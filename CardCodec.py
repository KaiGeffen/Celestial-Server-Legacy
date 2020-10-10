import copy

from logic.Catalog import all_cards
from logic.Recap import Recap
from logic.Effects import Status

# DELIM1 separates the elements of the largest data structure (ex: Recap)
# DELIM2 separates the individual entries of the lower level data struct (ex: List of cards)
DELIM1 = '¡'
DELIM2 = '™'
DELIM_DYN_TEXT = '£'


# Encode / Decode methods for sending the decklist to server
def encode_card(card):
    card_id = 0
    for catalog_entry in all_cards:
        if card.name == catalog_entry.name:
            if card.dynamic_text:
                return str(card_id) + DELIM_DYN_TEXT + card.dynamic_text
            else:
                return str(card_id)
        else:
            card_id += 1
    print(f"Encoding error for card {card}")
    raise Exception('Card encoding broken')

def encode_deck(deck):
    return DELIM2.join(list(map(encode_card, deck)))

def decode_card(s):
    sections = s.split(DELIM_DYN_TEXT)

    card_id = int(sections[0])
    dynamic_text = sections[1] if len(sections) > 1 else None

    card = all_cards.__getitem__(card_id)
    if dynamic_text:
        card = copy.deepcopy(card)
        card.text = dynamic_text

    return card

def decode_deck(deck_codes):
    if deck_codes:
        cards = deck_codes.split(DELIM2)
        return list(map(decode_card, cards))
    else:
        return []


def encode_stack(stack):
    def encode_play(play):
        card_id, owner = play
        return f'{encode_card(card_id)}{DELIM2}{owner}'

    result = DELIM1.join(list(map(encode_play, stack)))
    return result


def decode_stack(s):
    # If the stack is empty, return empty list
    if not s:
        return []

    plays = s.split(DELIM1)

    def decode_play(play: str):
        l = play.split(DELIM2)

        card = decode_card(l[0])
        owner = int(l[1])

        return card, owner

    return list(map(decode_play, plays))


def encode_recap(recap):
    result = f'{recap.sums[0]}{DELIM2}{recap.sums[1]}{DELIM1}{recap.wins[0]}{DELIM2}{recap.wins[1]}'

    # If no plays happened, just return the sums and wins
    # Otherwise, add a semicolon before the recap
    if not recap.story:
        return result
    else:
        result += DELIM1

    # Encode a single play of the recap, including textual description of what happened
    def encode_play(play):
        card, owner, text = play
        return f'{encode_card(card)}{DELIM2}{owner}{DELIM2}{text}'

    result += DELIM1.join(list(map(encode_play, recap.story)))
    return result


def decode_recap(s):
    recap = s.split(DELIM1, maxsplit=2)
    sums = list(map(int, recap[0].split(DELIM2)))
    wins = list(map(int, recap[1].split(DELIM2)))

    # If no plays happened, just return sums and wins recap
    if len(recap) == 2:
        return Recap(sums=sums, wins=wins)

    plays = recap[2].split(DELIM1)

    def decode_play(play: str):
        l = play.split(DELIM2)

        card = decode_card(l[0])
        owner = int(l[1])
        text = l[2]

        return card, owner, text

    story = list(map(decode_play, plays))
    return Recap(story=story, sums=sums, wins=wins)


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
        if c is '1':
            mulligans.append(True)
        elif c is '0':
            mulligans.append(False)
        else:
            raise Exception(f'Invalid mulligans: {s}')

    return mulligans
