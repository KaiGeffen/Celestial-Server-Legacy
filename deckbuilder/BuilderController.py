from cocos.director import director
from cocos.layer import Layer
from cocos.scene import Scene
import pyglet
import os.path

from deckbuilder.BuilderView import BuilderView
import GameController
import CardCodec
from logic import Catalog

from internet.Settings import SINGLE_PLAYER

DECK_FILE = 'saved_decks.txt'

UNFILTER = -1

class BuilderController(Layer):
    is_event_handler = True  #: enable pyglet's events

    def __init__(self, view):
        super().__init__()

        self.view = view

        # If file doesn't exist, create it
        if not os.path.isfile(DECK_FILE):
            with open(DECK_FILE, 'x') as file:
                pass

        # Read all saved decks from a file, store them in a list, with the initial element empty followed by older decks
        with open(DECK_FILE, 'r') as reader:
            # Read each past deck from file
            self.saved_decks = list(map(CardCodec.decode_deck, reader.readlines()))

            # Append an empty deck for current deck
            self.saved_decks.append([])

            self.remembered_deck_id = len(self.saved_decks) - 1

    def on_key_press(self, symbol, modifiers):
        # If choice is a number, show only cards with that cost
        choice = get_choice(symbol)
        if choice is not None: self.filter_catalog(choice)

        # Up/Down scan through saved decklists
        if symbol is pyglet.window.key.UP:
            if self.remembered_deck_id > 0:
                self.remembered_deck_id -= 1

                new_deck = self.saved_decks[self.remembered_deck_id]
                self.view.set_deck(new_deck)
            else:
                self.view.alert()

        if symbol is pyglet.window.key.DOWN:
            if self.remembered_deck_id < len(self.saved_decks) - 1:
                self.remembered_deck_id += 1

                new_deck = self.saved_decks[self.remembered_deck_id]
                self.view.set_deck(new_deck)
            else:
                self.view.alert()

        def save_deck(deck):
            with open(DECK_FILE, 'a') as writer:
                writer.write(CardCodec.encode_deck(deck) + '\n')

        # Save the deck, launch the main game
        if symbol is pyglet.window.key.SPACE:
            if self.view.is_ready():
                deck = self.view.get_deck()
                save_deck(deck)

                game_scene = GameController.get_new_game(deck, single_player=SINGLE_PLAYER)
                director.run(game_scene)

        if symbol is pyglet.window.key.S:
            deck = self.view.get_deck()
            save_deck(deck)

            # Add this deck to the saved decklists
            self.saved_decks[-1] = deck
            self.saved_decks.append([])

            # Point to the new deck entry
            self.remembered_deck_id = len(self.saved_decks) - 2

        if symbol is pyglet.window.key.RIGHT:
            self.view.scroll(right=True)
        if symbol is pyglet.window.key.LEFT:
            self.view.scroll(right=False)

    def on_mouse_motion(self, x, y, buttons, modifiers):
        self.view.on_mouse_motion(x, y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.view.on_mouse_press(x, y)

    # Filter the catalog to only have cards which cost the given amount
    def filter_catalog(self, cost):
        if cost == UNFILTER:
            catalog = Catalog.full_catalog
        else:
            def filter_by_cost(card):
                return card.cost == cost

            catalog = list(filter(filter_by_cost, Catalog.full_catalog))

        self.view.set_catalog(catalog)
    # # When a player has selected a card to play, or pass
    # def on_choice(self, card_num):
    #     if card_num is None:
    #         return
    #
    #     self.queued_act = card_num


# TODO Passing the scene through like this instead of using the scene queueing
# is only necessary because scene queueing seems to be broken (From reading it)
# Inherit from it, and fix it so that this sloppy scene-passing isn't permanent
def get_scene():
    scene = Scene()

    view = BuilderView(Catalog.full_catalog)
    controller = BuilderController(view)

    scene.add(controller, z=1, name="controller")
    scene.add(view, z=2, name="view")

    return scene


def get_choice(symbol):
    d = {
        pyglet.window.key._0: 0,
        pyglet.window.key._1: 1,
        pyglet.window.key._2: 2,
        pyglet.window.key._3: 3,
        pyglet.window.key._4: 4,
        pyglet.window.key._5: 5,
        pyglet.window.key._6: 6,
        pyglet.window.key._7: 7,
        pyglet.window.key._8: 8,
        pyglet.window.key._9: 9,
        pyglet.window.key.BACKSPACE: UNFILTER
    }
    return d.get(symbol, None)
