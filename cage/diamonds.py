#!/usr/local/bin/python
#
# $Id: //projects/cage/diamonds.py#7 $ $Date: 2002/12/07 $

"""
A simple reduction automaton that generates diamond patterns.
"""

__package__ = 'cage'


import curses
import operator

import cage


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        map = cage.VonNeumannMap(player.size)
        automaton = cage.TwoStateReductionAutomaton(map, operator.or_) 
        cage.SeedInitializer(5).initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
