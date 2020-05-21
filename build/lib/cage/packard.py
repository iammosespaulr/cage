#!/usr/local/bin/python
#
# $Id: //projects/cage/packard.py#8 $ $Date: 2006/05/14 $

"""
An implementation of Packard's automaton.
"""

__package__ = 'cage'


import curses

import cage


class PackardAutomaton(cage.SynchronousAutomaton):
    
    states = 256

    def __init__(self, size):
        cage.SynchronousAutomaton.__init__(self, cage.MooreMap(size))
    
    def rule(self, address):
        return divmod(self.map.inclusiveSum(address), 9)[0]


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = PackardAutomaton(player.size)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
