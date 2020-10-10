from cocos.text import Label
from cocos.layer import ColorLayer

from logic.Catalog import hidden_card

from view.Settings import *
from view.Shared import BaseView


class GameView(BaseView):
    def __init__(self, hud):
        super().__init__()

        self.hud = hud

        self.hand_layer = HandLayer()
        self.add(self.hand_layer)

        self.opp_hand_layer = OppHandLayer()
        self.add(self.opp_hand_layer)

        self.pile_layer = PileLayer()
        self.add(self.pile_layer)

        self.stack_layer = StackLayer()
        self.add(self.stack_layer)

        self.recap_layer = RecapLayer()
        self.add(self.recap_layer)

        self.deck_layer = DeckLayer()
        self.add(self.deck_layer)

        self.inventory_layer = InventoryLayer()
        self.add(self.inventory_layer)

        self.all_layers = [self.hand_layer,
                           self.opp_hand_layer,
                           self.stack_layer,
                           self.recap_layer,
                           self.deck_layer,
                           self.pile_layer,
                           self.inventory_layer]
        self.described_layers = [self.hand_layer,
                                 self.stack_layer,
                                 self.pile_layer,
                                 self.recap_layer,
                                 self.inventory_layer]
        self.recap_layer.visible = False
        self.inventory_layer.visible = False

    def on_mouse_motion(self, x, y):
        card = None
        for layer in self.described_layers:
            if layer.visible:
                found_card = layer.get_card_at_pos(x, y)
                if found_card:
                    card = found_card

        self.update_hover_text(card, x, y)

    def on_mouse_press(self, x, y):
        return self.hand_layer.get_card_number(x, y)

    def toggle_recap(self):
        if self.recap_layer.visible:
            self.recap_layer.visible = False
            self.stack_layer.visible = True
            self.deck_layer.visible = True
            self.pile_layer.visible = True
            self.inventory_layer.visible = False
        else:
            self.recap_layer.visible = True
            self.stack_layer.visible = False
            self.deck_layer.visible = True
            self.pile_layer.visible = True
            self.inventory_layer.visible = False

    def toggle_piles(self):
        if self.inventory_layer.visible:
            self.recap_layer.visible = False
            self.stack_layer.visible = True
            self.deck_layer.visible = True
            self.pile_layer.visible = True
            self.inventory_layer.visible = False
        else:
            self.recap_layer.visible = False
            self.stack_layer.visible = False
            self.deck_layer.visible = False
            self.pile_layer.visible = False
            self.inventory_layer.visible = True

    # Display the current game-state as described by model
    def display(self, model):
        self.hud.display(model)

        for layer in self.all_layers:
            layer.display(model)

        if self.recap_layer.visible:
            self.toggle_recap()

        if self.inventory_layer.visible:
            self.toggle_piles()

    # Alert player they did something invalid
    def alert(self):
        self.hud.alert()


# Layer for showing my (player 1) hand, and handling any interaction with it
class HandLayer(BaseView):
    def display(self, model):
        # Remove all cards
        for card in self.cards:
            self.remove(card)
        self.cards = []

        # Add all the cards in hand
        i = 0
        for card in model.hand:
            self.add_card(card, self.get_card_pos(i))
            i += 1

    # Get the number (Index in hand) of the card clicked on
    def get_card_number(self, x, y):
        i = 0

        for card in self.cards:
            if card.contains_point(x, y):
                return i
            i += 1

        return None

    # Get the positions for the nth card
    @staticmethod
    def get_card_pos(index):
        x = CELL_WIDTH / 2 + (CELL_WIDTH + WIDTH_BETWEEN) * index
        y = CELL_HEIGHT / 2
        return x, y


# Layer for showing opponent's hand, and handling any interaction with it
class OppHandLayer(BaseView):
    def display(self, model):
        # Remove all cards
        for card in self.cards:
            self.remove(card)
        self.cards = []

        # Add all the cards in hand
        i = 0
        for _ in range(model.opp_hand):
            self.add_card(hidden_card, self.get_card_pos(i))
            i += 1

    # Get the positions for the nth card
    @staticmethod
    def get_card_pos(index):
        x = CELL_WIDTH / 2 + (CELL_WIDTH + WIDTH_BETWEEN) * index
        y = WINDOW_HEIGHT - CELL_HEIGHT / 2
        return x, y


# Current stack for this round
class StackLayer(BaseView):
    def __init__(self):
        super().__init__()

        red_bar = ColorLayer(*BAR_COLOR, width=WINDOW_WIDTH, height=BAR_HEIGHT)
        red_bar.y = WINDOW_HEIGHT / 2 - BAR_HEIGHT / 2
        self.add(red_bar, z=-1)

    def display(self, model):
        # Remove all cards
        for card in self.cards:
            self.remove(card)
        self.cards = []

        # Add all the cards in hand
        i = 0
        for (card, owner) in model.stack:
            self.add_card(card, self.get_card_pos(i, owner))
            i += 1

    # Get the position of the nth card given its owner
    @staticmethod
    def get_card_pos(index, owner):
        x = CELL_WIDTH / 2 + (CELL_WIDTH - STACK_OVERLAP) * index

        if owner == 0:
            y = WINDOW_HEIGHT / 2 - STACK_OFFSET
        else:
            y = WINDOW_HEIGHT / 2 + STACK_OFFSET
        return x, y


# Recap of the last round
class RecapLayer(BaseView):
    def __init__(self):
        super().__init__()

        self.recap_labels = []

        red_bar = ColorLayer(*BAR_COLOR, width=WINDOW_WIDTH, height=BAR_HEIGHT)
        red_bar.y = WINDOW_HEIGHT / 2 - BAR_HEIGHT / 2
        self.add(red_bar, z=-1)

    def display(self, model):
        # Remove all cards
        for card in self.cards:
            self.remove(card)
        self.cards = []

        for label in self.recap_labels:
            self.remove(label)
            self.recap_labels = []

        self.add_recap_objects(model.recap)

    # Add all recap visual objects
    def add_recap_objects(self, recap):
        index = 0
        for (card, owner, play_text) in recap.story:
            pos = self.get_card_pos(index, owner)
            self.add_card(card, pos)

            if owner == 0:
                label = Label(play_text,
                              font_size=12,
                              color=(0, 255, 0, 255),
                              anchor_x='center',
                              anchor_y='top',
                              align='center',
                              width=RECAP_TEXT_WIDTH,
                              multiline=True)
                y = pos[1] - CELL_HEIGHT / 2
            else:
                label = Label(play_text,
                              font_size=14,
                              color=(0, 255, 0, 255),
                              anchor_x='center',
                              anchor_y='bottom',
                              align='center',
                              width=RECAP_TEXT_WIDTH,
                              multiline=True)
                y = pos[1] + CELL_HEIGHT / 2

            label.position = (pos[0], y)

            self.recap_labels.append(label)
            self.add(label)

            index += 1

        # Add the final scores - use the existing index to tell distance
        for player in (0, 1):
            text = f"{recap.sums[player]}"
            text += "*" * recap.wins[player]

            sum_label = Label(text,
                              font_size=24,
                              color=(255, 255, 0, 255),
                              anchor_x='center',
                              anchor_y='center',
                              align='center',
                              width=RECAP_TEXT_WIDTH,
                              multiline=True)
            sum_label.position = self.get_card_pos(index, player)

            self.recap_labels.append(sum_label)
            self.add(sum_label)

    # Get the position of the nth card given its owner
    @staticmethod
    def get_card_pos(index, owner):
        x = CELL_WIDTH / 2 + (CELL_WIDTH - STACK_OVERLAP) * index

        if owner == 0:
            y = WINDOW_HEIGHT / 2 - STACK_OFFSET
        else:
            y = WINDOW_HEIGHT / 2 + STACK_OFFSET
        return x, y


# Layer for both decks, with counts displayed on top
class DeckLayer(BaseView):
    def __init__(self):
        super().__init__()

        self.add_card(hidden_card, DECK_POS)
        self.label1 = Label('0',
                            font_size=TEXT_SIZE * 2,
                            color=(255, 0, 255, 255),
                            anchor_x='center',
                            anchor_y='center')
        self.label1.position = DECK_POS
        self.add(self.label1)

        self.add_card(hidden_card, OPP_DECK_POS)
        self.label2 = Label('0',
                            font_size=TEXT_SIZE * 2,
                            color=(255, 0, 255, 255),
                            anchor_x='center',
                            anchor_y='center')
        self.label2.position = OPP_DECK_POS
        self.add(self.label2)

    def display(self, model):
        # For each deck, display if not empty
        if model.deck:
            self.cards[0].visible = True
            self.label1.element.text = f'{len(model.deck)}'
        else:
            self.cards[0].visible = False
            self.label1.element.text = ''

        if model.opp_deck > 0:
            self.cards[1].visible = True
            self.label2.element.text = f'{model.opp_deck}'
        else:
            self.cards[1].visible = False
            self.label2.element.text = ''


# Layer for both discard piles, showing the top card of pile if applicable
class PileLayer(BaseView):
    def __init__(self):
        super().__init__()

        self.label1 = Label('0',
                            font_size=TEXT_SIZE * 2,
                            color=(255, 0, 255, 255),
                            anchor_x='center',
                            anchor_y='center')
        self.label1.position = PILE_POS
        self.add(self.label1, 2)

        self.label2 = Label('0',
                            font_size=TEXT_SIZE * 2,
                            color=(255, 0, 255, 255),
                            anchor_x='center',
                            anchor_y='center')
        self.label2.position = OPP_PILE_POS
        self.add(self.label2, 2)

    def display(self, model):
        # Remove all cards
        for card in self.cards:
            self.remove(card)
        self.cards = []

        # For each pile, add the top card as image
        if model.pile[0]:
            card = model.pile[0][-1]
            self.add_card(card, PILE_POS)
            self.label1.element.text = f'{len(model.pile[0])}'
        else:
            self.label1.element.text = ''

        if model.pile[1]:
            card = model.pile[1][-1]
            self.add_card(card, OPP_PILE_POS)
            self.label2.element.text = f'{len(model.pile[1])}'
        else:
            self.label2.element.text = ''


# Your remaining deck, your and opponent's discard piles
class InventoryLayer(BaseView):
    def display(self, model):
        # Remove all cards
        for card in self.cards:
            self.remove(card)
        self.cards = []

        # For each of your deck, your pile, opponent's pile, display each card
        d = {0: model.deck,
             1: model.pile[0],
             2: model.pile[1]}
        for zone in range(3):
            i = 0
            for card in d[zone]:
                self.add_card(card, self.get_card_pos(i, zone))
                i += 1

    # Get the position of the nth card given its zone (deck, your pile, opp pile)
    @staticmethod
    def get_card_pos(index, zone):

        # Offset from the left side, for opponent but opposite for you
        x = CELL_WIDTH / 2 + (CELL_WIDTH - STACK_OVERLAP) * index
        if not zone == 2:
            x = WINDOW_WIDTH - x

        if zone == 0:
            y = WINDOW_HEIGHT / 2 - CELL_HEIGHT - HEIGHT_BETWEEN
        elif zone == 1:
            y = WINDOW_HEIGHT / 2
        else:
            y = WINDOW_HEIGHT / 2 + CELL_HEIGHT + HEIGHT_BETWEEN
        return x, y


"""
class GameView(BaseView):
    def __init__(self, hud):
        super().__init__()

        # CardSprites, which extend sprite to also include the card being displayed
        self.hand = []
        self.opp_hand = []
        self.stack = []

        self.recap = []
        self.recap_labels = []

        # Toggleable sprites for the info you have
        self.deck = []
        self.pile = []
        self.opp_pile = []

        self.hud = hud

    # Display the current game-state as described by model
    def display(self, model):
        self.remove_all_objects()
        self.add_all_objects(model)

        self.hud.display(model)

    # Return the index of the card clicked on
    def on_mouse_press(self, x, y):
        # TODO is very similar to below get_card, consider merging
        index = 0
        for sprite in self.hand:
            if sprite.contains_point(x, y):
                return index
            index += 1

        return None

    # Toggle between whether recap from last round is visible, or current round is visible
    def toggle_recap(self):
        d = {0 : 255, 255 : 0}

        for obj in self.recap + self.stack + self.recap_labels:
            obj.opacity = d[obj.opacity]

    # Return a card which is at given position
    def get_card_at_pos(self, x, y):
        for sprite in self.hand + self.stack + self.recap + self.opp_hand:
            if sprite.opacity > 0 and sprite.contains_point(x, y):
                return sprite.card

        # Hovering over nothing
        return None

    # Add all visual objects as described by model
    def add_all_objects(self, model):
        index = 0
        for card in model.hand:
            x = self.get_card_x(index)
            y = CELL_HEIGHT / 2
            self.add_card(card, (x,y), self.hand)

            index += 1

        for index in range(0, model.opp_hand):
            x = self.get_card_x(index)
            y = WINDOW_HEIGHT - CELL_HEIGHT / 2
            self.add_card(hidden_card, (x,y), self.opp_hand)

        index = 0
        for (card, owner) in model.stack:
            pos = self.get_stack_card_pos(index, owner)
            self.add_card(card, pos, self.stack)

            index += 1

        # Recap, which will start out opaque, until tab is pressed
        self.add_recap_objects(model.recap)

    # Add all recap visual objects
    def add_recap_objects(self, recap):
        index = 0
        for (card, owner, play_text) in recap.story:
            pos = self.get_stack_card_pos(index, owner)
            self.add_card(card, pos, self.recap, invisible=True)

            y = 0
            if owner == 0:
                label = Label(play_text,
                              font_size=14,
                              color=(0, 255, 0, 255),
                              anchor_x='center',
                              anchor_y='top',
                              align='center',
                              width=RECAP_TEXT_WIDTH,
                              multiline=True)
                y = pos[1] - CELL_HEIGHT / 2
            else:
                label = Label(play_text,
                              font_size=14,
                              color=(0, 255, 0, 255),
                              anchor_x='center',
                              anchor_y='bottom',
                              align='center',
                              width=RECAP_TEXT_WIDTH,
                              multiline=True)
                y = pos[1] + CELL_HEIGHT / 2

            label.position = (pos[0], y)
            label.opacity = 0

            self.recap_labels.append(label)
            self.add(label)

            index += 1

        # Add the final scores - use the existing index to tell distance
        for player in (0, 1):
            text = f"{recap.sums[player]}"
            text += "*" * recap.wins[player]

            sum_label = Label(text,
                              font_size=24,
                              color=(255, 255, 0, 255),
                              anchor_x='center',
                              anchor_y='center',
                              align='center',
                              width=RECAP_TEXT_WIDTH,
                              multiline=True)
            sum_label.position = self.get_stack_card_pos(index, player)
            sum_label.opacity = 0

            self.recap_labels.append(sum_label)
            self.add(sum_label)

    # Remove all visual objects
    def remove_all_objects(self):
        for spr in self.hand:
            self.remove(spr)
        self.hand = []

        for spr in self.opp_hand:
            self.remove(spr)
        self.opp_hand = []

        for spr in self.stack:
            self.remove(spr)
        self.stack = []

        for spr in self.recap:
            self.remove(spr)
        self.recap = []

        for label in self.recap_labels:
            self.remove(label)
        self.recap_labels = []

    

    # Get the pos of nth card if owners plays it
    @staticmethod
    def get_stack_card_pos(index, owner):
        x = CELL_WIDTH / 2 + (CELL_WIDTH - STACK_OVERLAP) * index

        if owner == 0:
            y = WINDOW_HEIGHT / 2 - STACK_OFFSET
        else:
            y = WINDOW_HEIGHT / 2 + STACK_OFFSET
        return (x, y)
"""