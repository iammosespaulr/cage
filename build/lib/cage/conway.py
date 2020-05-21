#!/usr/local/bin/python
#
# $Id: //projects/cage/conway.py#10 $ $Date: 2002/12/07 $

"""
An implementation of Conway's Game of Life, really just a specialization of
a two-state totalistic automaton.
"""

__package__ = 'cage'


import curses

import cage


rPentomino = [[0, 1, 1],
              [1, 1, 0],
              [0, 1, 0]]


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = cage.ConwayAutomaton(player.size)
        cage.PatternInitializer(rPentomino).initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
