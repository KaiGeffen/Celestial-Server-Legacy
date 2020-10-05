from cocos.layer import *
from cocos.text import *
from cocos.actions import *
from cocos.sprite import Sprite

from logic.Catalog import hidden_card
from logic.Effects import Status

from view.Settings import *
from view.Shared import BaseView

# TODO connect this with the const in gameview
HAND_HEIGHT = 120
TEXT_BUFFER = 12

class ManaLayer(Layer):
    def __init__(self):
        super().__init__()
        w, h = director.get_window_size()

        self.mana1 = Label('Mana:', font_size=TEXT_SIZE,
                           color=(255,255,255,255),
                           anchor_x='right',
                           anchor_y='bottom')
        self.mana1.position = (w, 0)
        self.add(self.mana1)

        self.mana2 = Label('Mana:', font_size=TEXT_SIZE,
                           color=(255, 255, 255, 255),
                           anchor_x='right',
                           anchor_y='top')
        self.mana2.position = (w, h)
        self.add(self.mana2)

        self.position = (0, 0)

    def draw(self):
        super().draw()

    def display(self, model):
        self.mana1.element.text = f'Mana: {model.mana} / {model.max_mana[0]}'
        self.mana2.element.text = f'Mana: ? / {model.max_mana[1]}'


class ScoreLayer(Layer):
    def __init__(self):
        super().__init__()
        w, h = director.get_window_size()

        self.score1 = Label('Score: 0', font_size=TEXT_SIZE,
                           color=(255, 255, 255, 255),
                           anchor_x='right',
                           anchor_y='bottom')
        self.score1.position = (w, TEXT_SIZE + TEXT_BUFFER)
        self.add(self.score1)

        self.score2 = Label('Score:0', font_size=TEXT_SIZE,
                           color=(255, 255, 255, 255),
                           anchor_x='right',
                           anchor_y='top')
        self.score2.position = (w, h - TEXT_SIZE - TEXT_BUFFER)
        self.add(self.score2)

        self.position = (0, 0)

    def draw(self):
        super().draw()

    def display(self, model):
        self.score1.element.text = f'Score: {model.wins[0]}'
        self.score2.element.text = f'Score: {model.wins[1]}'


class StatusLayer(Layer):
    def __init__(self):
        super().__init__()
        w, h = director.get_window_size()

        self.status1 = Label('Status:', font_size=TEXT_SIZE,
                           color=STATUS_COLOR,
                           anchor_x='right',
                           anchor_y='bottom')
        self.status1.position = (w, (TEXT_SIZE + TEXT_BUFFER) * 2)
        self.add(self.status1)

        self.status2 = Label('Status:', font_size=TEXT_SIZE,
                           color=STATUS_COLOR,
                           anchor_x='right',
                           anchor_y='top')
        self.status2.position = (w, h - (TEXT_SIZE + TEXT_BUFFER) * 2)
        self.add(self.status2)

        self.position = (0, 0)

    def draw(self):
        super().draw()

    def display(self, model):
        def get_status_text(statuses):
            result = ''

            for status_type in Status:
                count = statuses.count(status_type)
                if count:
                    result += f'{status_type.value} {count}, '

            result = result.rstrip(', ')
            return result

        self.status1.element.text = get_status_text(model.status)
        self.status2.element.text = get_status_text(model.opp_status)


class PriorityLayer(Layer):
    def __init__(self):
        super().__init__()
        w, h = director.get_window_size()

        self.add(ColorLayer(180, 180, 180, 200, width=w, height=HAND_HEIGHT))

        self.p1_pos = (0, 0)
        self.p2_pos = (0, h - HAND_HEIGHT)
        self.position = self.p1_pos

    def draw(self):
        super().draw()

    def display(self, model):
        if model.priority == 0:
            self.position = self.p1_pos
        else:
            self.position = self.p2_pos


class HUD(BaseView):
    def __init__(self):
        super().__init__(color=True)
        self.mana_layer = ManaLayer()
        self.add(self.mana_layer)

        self.score_layer = ScoreLayer()
        self.add(self.score_layer)

        self.status_layer = StatusLayer()
        self.add(self.status_layer)

        self.priority_layer = PriorityLayer()
        self.add(self.priority_layer, z=1)

    def display(self, model):
        self.mana_layer.display(model)
        self.score_layer.display(model)
        self.status_layer.display(model)
        self.priority_layer.display(model)
