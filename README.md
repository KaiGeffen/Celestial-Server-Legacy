# Celestial
A card game that I work on sporadically. 

Can be played by a single person against AI opponent, or 2 players locally or over a connection (LAN easy, over the wider internet also pretty easy if you can setup port-forwarding).

For the moment, I have not prioritized making it easy for you to setup and play. If you do want to play it, go through these steps:
/*:
1. Download pycharm: https://www.jetbrains.com/pycharm/
2. Launch pycharm, open the Celestial project.
3. Preferences > Project: Celestial > Project Interpreter
4. Make sure that the interpreter is Python 3.7, and add the packages (bottom left '+' button) pyglet 1.5.5 and cocos2d 0.6.8
5. If playing locally, go to *Run* then *Run clients + server*, build decks for both players, then in 1 window press *a* to autoplay.
6. If playing remotely, change the internet > settings python-file. Run main.py on each player's machine, run server.py on whichever machine is serving.
*/

# Credit
All icons come from https://game-icons.net/, under a CC BY 3.0 license: https://creativecommons.org/licenses/by/3.0/

They are made by Lorc, Delapouite, and more.

For a full list of contributors, see https://game-icons.net/about.html#authors

# Deckbuilder
Press left/right to navigate

Up/Down go through previously used or saved (Press *S* to save a deck in progress) decks

Press 0-9 to filter the cards by cost, *delete* to see all cards

Hover over a card to see what it does, click to add it to deck, click it in the deck below to remove it

Hit *space* once you have a full deck (15 cards unless you are a cheater)

# Rules
Highlighted player has priority, they either play a card from hand (click or 1-6 keyboard) or pass

Playing a card consumes mana and puts in on the stack

A round goes until both players pass in a row

At that point the points for that round are calculated and the player with more gets 1 _round-win_

At turn start, each player draws 2 cards (capped at 6) and gets 1 max mana (Up to 10)

Press *d* to see your deck and both player's discards piles

Press *tab* to see how the last round went

First player to 5 round-wins who also is ahead by at least 2 round-wins is victorious

It won't tell you, but you and I will know.
