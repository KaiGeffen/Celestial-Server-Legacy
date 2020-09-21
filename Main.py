from cocos.director import director

from deckbuilder import BuilderController
import FP
from view import Settings


def main():
    director.init(width=Settings.WINDOW_WIDTH,
                  height=Settings.WINDOW_HEIGHT,
                  caption=Settings.WINDOW_TITLE)
    FP.do_fp_setup()

    # TODO Ideally, the scenes would be queued here for clarity
    # But since director's scene stack doesn't work, the next scene is called
    # explicitly in the builder controller, which really shouldn't be that coupled
    # and shouldn't see so high as to know about handling the next scene etc
    deck_builder_scene = BuilderController.get_scene()
    director.run(deck_builder_scene)


if __name__ == '__main__':
    main()
