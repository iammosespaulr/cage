#!/usr/local/bin/python
#
# $Id: //projects/cage/110.py#5 $ $Date: 2002/12/07 $

"""
Same 1D rule 110 displayer using PIL.  Note that the display does not
wrap or continue off to the left.
"""

__package__ = 'cage'


import cage


RULE = 110
RANDOM = 0


def main():
    player = None
    try:
        player = cage.ImagePlayer(400, 600)
        automaton = cage.LinearCodedAutomaton(player.size, RULE)
        rightMostAddress = player.size[0] - 1,
        if RANDOM:
            initializer = cage.RandomInitializer()
        else:
            initializer = cage.PointInitializer(rightMostAddress)
        initializer.initialize(automaton)
        player.main(automaton)
    finally:
        if player is not None:
            player.done()

if __name__ == '__main__': main()
