#!/usr/local/bin/python
#
# $Id: //projects/cage/parity.py#8 $ $Date: 2002/12/07 $

"""
An implementation of a trivial parity rule as a reduction automaton.
"""

__package__ = 'cage'


import curses
import operator

import cage


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        map = cage.VonNeumannMap(player.size)
        automaton = cage.TwoStateReductionAutomaton(map, operator.xor)
        cage.SeedInitializer(5).initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
