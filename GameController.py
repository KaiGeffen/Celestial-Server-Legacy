from cocos.layer import Layer
from cocos.scene import Scene
import pyglet

import _thread
import time

from view.GameView import GameView
from view.MulliganView import MulliganView
from view.HUD import HUD

from internet.Network import Network
import internet.Settings
import AI

# The number to use for client passing, arbitrary
PASS = 10
REFRESH_INTERVAL = 0.1


class GameController(Layer):
    is_event_handler = True  #: enable pyglet's events

    def __init__(self, net, view, mulligan_view):
        super().__init__()

        self.view = view
        self.mulligan_view = mulligan_view
        self.net = net

        # Model is set and updated from the network thread
        self.model = None
        self.queued_act = None

        self.mulligan_choices = [False, False, False]

        # Whether a redraw had been queued, set by the thread that listens for state changes from the server
        self.redraw_queued = False

        # Autoplay, which enables an ai to take all actions for the player. Toggle with A key
        self.autoplay = False

        # Hide all of the reminder text about cards, mostly to prevent overuse of cpu
        # Because each frame when mouse moves, each card in the environment must be checked
        # to see if there is an overlap (In the case where there isn't)
        self.disable_reminder_text = False

        _thread.start_new_thread(self.start_network_thread, ())

        def refresh_display(*args):
            if self.redraw_queued:
                self.view.display(self.model)
                self.redraw_queued = False

        self.schedule_interval(refresh_display, REFRESH_INTERVAL)

    # On response from network, set client's model to response, update view, and act if autoplay is enabled
    def start_network_thread(self):
        while True:
            new_state = self.net.get_state(self.model)

            if new_state:
                self.model = new_state
                self.redraw_queued = True

                # Since the state in which we decided on the action wasn't current, forget our choice
                self.queued_act = None

                # If the mulligan phase is now over, remove that scene
                if self.mulligan_view and new_state.mulligans_complete[0]:
                    self.mulligan_view.end()
                    # TODO The view still exists, try to remove it from the scene to handle cleanly, or make it toggleable to use elsewhere
                    self.mulligan_view = None

                # State changed and we now have priority, queue up a play
                if self.autoplay and new_state.priority == 0:
                    self.on_choice(AI.get_action(self.model))

            elif self.queued_act is not None:
                valid = self.net.send_action(self.queued_act)

                if not valid:
                    self.view.alert()
                    self.queued_act = None
                else:
                    self.queued_act = None

            time.sleep(internet.Settings.CLIENT_WAIT)

    def on_key_press(self, symbol, modifiers):
        # Tab key swaps view from current to recap, D toggles piles view
        if symbol is pyglet.window.key.TAB:
            self.view.toggle_recap()
            return
        if symbol is pyglet.window.key.D:
            self.view.toggle_piles()
            return
        # A toggles autoplay. When enabled, cards are played automatically by an ai
        if symbol is pyglet.window.key.A:
            self.autoplay = not self.autoplay
            self.on_choice(AI.get_action(self.model))
            return
        if symbol is pyglet.window.key.R:
            self.disable_reminder_text = not self.disable_reminder_text
            return

        card_num = get_choice(symbol)
        self.on_choice(card_num)

    def on_mouse_motion(self, x, y, buttons, modifiers):
        if not self.disable_reminder_text:
            self.view.on_mouse_motion(x, y)

    # If left-click, select a card, if right-click, pass turn
    def on_mouse_press(self, x, y, buttons, modifiers):
        if buttons & pyglet.window.mouse.LEFT:
            card_num = self.view.on_mouse_press(x, y)
            self.on_choice(card_num)
        elif buttons & pyglet.window.mouse.RIGHT:
            self.on_choice(PASS)

    # When a player has selected a card to play, or pass
    def on_choice(self, card_num):
        if card_num is None:
            return

        # If still in the mulligan phase, either toggle a mulligan or send the choices
        if not self.model.mulligans_complete[0]:
            if card_num is PASS:
                self.net.send_mulligans(self.mulligan_choices)
            elif card_num > 2:
                self.view.alert()
            else:
                self.mulligan_choices[card_num] = not self.mulligan_choices[card_num]
                self.mulligan_view.toggle(card_num)

        else:
            self.queued_act = card_num


def get_new_game(start_deck):
    scene = Scene()

    net = Network(start_deck)

    # Get the model from Server
    hud = HUD()
    view = GameView(hud)
    mulligan_view = MulliganView()
    controller = GameController(net, view, mulligan_view)

    scene.add(controller, z=1, name="controller")
    scene.add(hud, z=-2, name="hud")
    scene.add(mulligan_view, z=3, name='mulligan_view')
    scene.add(view, z=4, name="view")

    return scene


def get_choice(symbol):
    d = {
        pyglet.window.key._1: 0,
        pyglet.window.key._2: 1,
        pyglet.window.key._3: 2,
        pyglet.window.key._4: 3,
        pyglet.window.key._5: 4,
        pyglet.window.key._6: 5,
        pyglet.window.key._7: 6,
        pyglet.window.key._8: 7,
        pyglet.window.key._9: 8,
        pyglet.window.key._0: 9,
        pyglet.window.key.SPACE: PASS
    }
    return d.get(symbol, None)
