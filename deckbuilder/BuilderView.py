import cocos
import time

from view.Settings import *
from view.Shared import BaseView


class BuilderView(BaseView):
    def __init__(self, catalog):
        super().__init__(color=True)

        self.catalog_layer = CatalogView(catalog)
        self.add(self.catalog_layer)

        self.deck_layer = DeckView()
        self.add(self.deck_layer)

        self.described_layers = [self.catalog_layer, self.deck_layer]

    """Actions initiated by BuilderController"""
    def on_mouse_motion(self, x, y):
        card = None
        for layer in self.described_layers:
            if layer.visible:
                found_card = layer.get_card_at_pos(x, y)
                if found_card:
                    card = found_card

        self.update_hover_text(card, x, y)

    def on_mouse_press(self, x, y):
        # Remove card from deck if there is a card at that pos
        self.deck_layer.remove_card(x, y)

        # Clicked card was in catalog, add it to deck
        card = self.catalog_layer.get_card_at_pos(x, y)
        if card:
            added = self.deck_layer.add_card(card)
            if not added:
                self.alert()

        self.on_screen_change()

    # Scroll all cards in the catalog left/right
    def scroll(self, right):
        self.catalog_layer.scroll(right)

        self.hover_text.element.text = ''
        self.hover_background.visible = False

    # Set deck to the given deck
    def set_deck(self, new_deck):
        self.deck_layer.set_deck(new_deck)

        self.on_screen_change()

    # Set the catalog to given catalog
    def set_catalog(self, catalog):
        self.catalog_layer.set_catalog(catalog)

        self.on_screen_change()

    # Sort the active deck by cost
    def sort_deck(self):
        self.deck_layer.sort_deck()

    """Checks called by BuilderController"""
    # Called by outside method to see if deck is complete and ready to play
    def is_ready(self):
        return True
        #return len(self.deck) == MAX_DECK_SIZE

    # Called by outside method to get the fully composed deck
    def get_deck(self):
        return list(map((lambda a: a.card), self.deck_layer.cards))

    """Used internally"""
    # When the visible cards change, update the hover text to reflect that
    def on_screen_change(self):
        x, y = self.hover_text.position
        self.on_mouse_motion(x, y)


# The full catalog of cards the player can include in their deck
class CatalogView(BaseView):
    def __init__(self, cards):
        super().__init__()

        # The time at which scroll was last used, so that it has to wait to complete before being used again
        self.last_scroll = 0

        self.set_catalog(cards)

    def set_catalog(self, catalog):
        # Remove all cards
        for card in self.cards:
            self.remove(card)
        self.cards = []

        index = 0
        for card in catalog:
            self.add_card(card, self.get_card_pos(index))
            index += 1

    # Scroll all cards in the catalog left/right
    def scroll(self, right):
        # If the last scroll has not yet completed
        if self.last_scroll + TRANSITION_TIME > time.time():
            return

        self.last_scroll = time.time()

        if right:
            move = cocos.actions.MoveBy((WINDOW_WIDTH, 0), TRANSITION_TIME)
        else:
            move = cocos.actions.MoveBy((-WINDOW_WIDTH, 0), TRANSITION_TIME)

        for card in self.cards:
            card.do(move)

    # Calculate the position that the nth card should be
    @staticmethod
    def get_card_pos(index):
        page_num = index // CARDS_PER_PAGE
        x = WIDTH_BETWEEN + CELL_WIDTH / 2 + (index % CARDS_PER_ROW) * (CELL_WIDTH + WIDTH_BETWEEN) + page_num * WINDOW_WIDTH
        row_num = int((index % CARDS_PER_PAGE) / CARDS_PER_ROW)
        y = WINDOW_HEIGHT - HEIGHT_BETWEEN - CELL_HEIGHT / 2 - row_num * (HEIGHT_BETWEEN + CELL_HEIGHT)
        return x, y


# The current deck being built by the player
class DeckView(BaseView):
    # Display all cards in the deck
    def display(self):
        index = 0
        for card in self.cards:
            x = WINDOW_WIDTH - WIDTH_BETWEEN - CELL_WIDTH / 2 - index * (CELL_WIDTH - STACK_OVERLAP)
            y = HEIGHT_BETWEEN + CELL_HEIGHT / 2 + (index % 2) * STACK_OFFSET
            card.position = (x, y)

            index += 1

    def add_card(self, card, pos=(0, 0), invisible=False):
        if len(self.cards) < MAX_DECK_SIZE:
            super().add_card(card)
            self.display()

            return True
        else:
            return False

    def remove_card(self, x, y):
        # This gets the sprite, instead of the associated card, thus get_card_at_pos isn't called
        for spr in self.cards[::-1]:
            if spr.contains_point(x, y):
                self.cards.remove(spr)
                self.remove(spr)

                self.display()
                return True
        return False

    def set_deck(self, deck):
        # Clear current deck
        for card in self.cards:
            self.remove(card)
        self.cards = []

        for card in deck:
            self.add_card(card, (0, 0))

        self.display()

    # Sort the active deck by cost
    def sort_deck(self):
        cards = list(map(lambda sprite: sprite.card,
                         self.cards))

        def cost_then_alphabet(card):
            return card.cost + 1 / hash(card.name)

        cards.sort(key=cost_then_alphabet)

        self.set_deck(cards)

    # Calculate the position that the nth card should be
    @staticmethod
    def get_card_pos(self, index):
        page_num = index // CARDS_PER_PAGE
        x = WIDTH_BETWEEN + CELL_WIDTH / 2 + (index % CARDS_PER_ROW) * (CELL_WIDTH + WIDTH_BETWEEN) + page_num * WINDOW_WIDTH
        row_num = int((index % CARDS_PER_PAGE) / CARDS_PER_ROW)
        y = WINDOW_HEIGHT - HEIGHT_BETWEEN - CELL_HEIGHT / 2 - row_num * (HEIGHT_BETWEEN + CELL_HEIGHT)
        return x, y
