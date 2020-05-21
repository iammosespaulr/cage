#!/usr/local/bin/python
#
# $Id: //projects/cage/squares.py#8 $ $Date: 2003/04/23 $

"""
A simple reduction automaton that generates square patterns.
"""

__package__ = 'cage'


import curses
import operator

import cage


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        map = cage.MooreMap(player.size)
        automaton = cage.TwoStateReductionAutomaton(map, operator.or_) 
        cage.SeedInitializer(5).initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
