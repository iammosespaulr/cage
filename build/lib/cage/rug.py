#!/usr/local/bin/python
#
# $Id: //projects/cage/rug.py#2 $ $Date: 2006/05/14 $

"""
An implementation of the rug rule.
"""

__package__ = 'cage'


import curses

import cage


class RugAutomaton(cage.SynchronousAutomaton):
    
    states = 26

    def __init__(self, size):
        cage.SynchronousAutomaton.__init__(self, cage.MooreMap(size))
    
    def rule(self, address):
        return (self.map.average(address) + 1) % self.states


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = RugAutomaton(player.size)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
