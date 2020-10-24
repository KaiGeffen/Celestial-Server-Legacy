import cocos
from cocos.text import RichLabel
from cocos.actions import RotateBy

from view.Settings import *


# The basic view functionality common to all views
class BaseView(cocos.layer.ColorLayer):
    def __init__(self, color=False):
        if color:
            super().__init__(*BACKGROUND_COLOR)
        else:
            super().__init__(*NO_COLOR)

        self.original_opacity = self.opacity

        # List of all card sprites currently displayed
        self.cards = []

        # TODO Because many layers exist within a view that inherit from this, there are redundant hover texts, fix
        self.hover_text = RichLabel(' ',
                                    font_size=TEXT_SIZE,
                                    color=(255, 0, 0, 255),
                                    anchor_x='left',
                                    anchor_y='bottom',
                                    align='center',
                                    width=TEXT_WIDTH,
                                    multiline=True)
        self.add(self.hover_text, 2)

        self.hover_background = cocos.sprite.Sprite('White.png')
        self.hover_background.visible = False
        self.add(self.hover_background, 1)

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

            self.hover_background.visible = False
        else:
            self.hover_text.element.text = card.text
            self.hover_text.position = (x, y)

            self.hover_background.visible = True
            self.hover_background.position = (x, y)

            # Adjust anchoring so that text isn't outside of window
            if x < TEXT_WIDTH / 2:
                self.hover_text.element.anchor_x = 'left'
                self.hover_background.x += TEXT_WIDTH / 2
            elif x + TEXT_WIDTH / 2 > WINDOW_WIDTH:
                self.hover_text.element.anchor_x = 'right'
                self.hover_background.x -= TEXT_WIDTH / 2
            else:
                self.hover_text.element.anchor_x = 'center'

            # Adjust the y of background to fit the text
            text_height = self.hover_text.element.content_height
            line_height = 49
            text_lines = text_height / line_height
            self.hover_background.scale_y = text_lines

            if y > WINDOW_HEIGHT / 2:
                self.hover_text.element.anchor_y = 'top'
                self.hover_background.y -= text_height / 2
            else:
                self.hover_text.element.anchor_y = 'bottom'
                self.hover_background.y += text_height / 2

    # Add card at pos and remember it in ary
    def add_card(self, card, pos=(0, 0), invisible=False):
        sprite = CardSprite(card)
        sprite.position = pos
        sprite.scale = .25

        if invisible:
            sprite.opacity = 0

        self.cards.append(sprite)
        self.add(sprite)

        return sprite

    # Alert player they've done something wrong
    def alert(self):
        self.do(
            cocos.actions.FadeTo(0, .07) + cocos.actions.FadeTo(self.original_opacity, .07)
        )
        # cocos.actions.Waves(grid=(16, 12), duration=4) + cocos.actions.Liquid(grid=(16, 12), duration=5))


# A card as a sprite object
class CardSprite(cocos.sprite.Sprite):
    def __init__(self, card):
        super().__init__(f"{card.name}.png")

        self.card = card

    # The existing 'contains' method for Sprites seems to not be working
    def contains_point(self, x, y):
        if x < self.x - CELL_WIDTH_HALF or x > self.x + CELL_WIDTH_HALF:
            return False
        if y < self.y - CELL_HEIGHT_HALF or y > self.y + CELL_HEIGHT_HALF:
            return False
        return True

    # Visually shake the card
    def shake(self):
        pass
        # action = RotateBy(3, .1) + (RotateBy(-6, .2) + RotateBy(6, .2)) * 3 + RotateBy(-3, .1)
        # self.do(action)

    # Visually shake the card
    def shake(self):
        pass
        # action = RotateBy(3, .1) + (RotateBy(-6, .2) + RotateBy(6, .2)) * 3 + RotateBy(-3, .1)
        # self.do(action)
