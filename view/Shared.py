import cocos

from cocos.text import Label
from view.Settings import *


# The basic view functionality common to all views
class BaseView(cocos.layer.ColorLayer):
    def __init__(self, color=False):
        if color:
            super().__init__(*BACKGROUND_COLOR)
        else:
            super().__init__(*NO_COLOR)

        # List of all card sprites currently displayed
        self.cards = []

        # TODO Because many layers exist within a view that inherit from this, there are redundant hover texts, fix
        self.hover_text = Label('',
                                font_size=TEXT_SIZE,
                                color=(255, 0, 0, 255),
                                anchor_x='left',
                                anchor_y='bottom',
                                align='center',
                                width=TEXT_WIDTH,
                                multiline=True)

        self.add(self.hover_text, 1)

    # Return a card at the position, from among this views cards and the extra cards provided. Pref later cards
    def get_card_at_pos(self, x, y, extra=[]):
        for sprite in self.cards[::-1] + extra:
            if sprite.contains_point(x, y):
                return sprite.card

    # Update hover text to explain card and be at (x,y)
    def update_hover_text(self, card, x, y):
        if not card:
            self.hover_text.element.text = ''
            self.hover_text.position = (x, y)
        else:
            self.hover_text.element.text = card.text
            self.hover_text.position = (x, y)

            # Adjust anchoring so that text isn't outside of window
            if x < TEXT_WIDTH / 2:
                self.hover_text.element.anchor_x = 'left'
            elif x + TEXT_WIDTH / 2 > WINDOW_WIDTH:
                self.hover_text.element.anchor_x = 'right'
            else:
                self.hover_text.element.anchor_x = 'center'

            if y > WINDOW_HEIGHT / 2:
                self.hover_text.element.anchor_y = 'top'
            else:
                self.hover_text.element.anchor_y = 'bottom'

    # Add card at pos and remember it in ary
    def add_card(self, card, pos=(0, 0), invisible=False):
        sprite = CardSprite(card)
        sprite.position = pos
        sprite.scale = .25

        if invisible:
            sprite.opacity = 0

        self.cards.append(sprite)
        self.add(sprite)


# A card as a sprite object
class CardSprite(cocos.sprite.Sprite):
    def __init__(self, card):
        super().__init__(f"{card.name}.png")

        self.card = card

    # The existing 'contains' method for Sprites seems to not be working
    def contains_point(self, x, y):
        if x < self.x - CELL_WIDTH / 2 or x > self.x + CELL_WIDTH / 2:
            return False
        if y < self.y - CELL_HEIGHT / 2 or y > self.y + CELL_HEIGHT / 2:
            return False
        return True
