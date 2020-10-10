from cocos.text import Label
from cocos.layer import ColorLayer

from view.Settings import *
from view.Shared import BaseView
from view.GameView import HandLayer


# View which shows all elements of the mulligan phase
class MulliganView(BaseView):
    def __init__(self):
        super().__init__()

        self.label = Label('Mulligan',
                           font_size=TEXT_SIZE * 2,
                           color=(255, 0, 255, 255),
                           anchor_x='center',
                           anchor_y='center')
        self.label.position = MULLIGAN_POSITION
        self.add(self.label)

        self.highlights = []
        for i in range(3):
            highlight = ColorLayer(*HIGHLIGHT_COLOR, width=HIGHLIGHT_WIDTH, height=HIGHLIGHT_HEIGHT)
            highlight.position = HandLayer.get_card_pos(i)
            highlight.visible = False

            self.add(highlight, z=-1)

            self.highlights.append(highlight)

    def display(self, mulligans):
        for i in range(len(mulligans)):
            self.highlights[i].visible = mulligans[i]
