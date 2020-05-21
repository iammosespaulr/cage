#!/usr/local/bin/python
#
# $Id: //projects/cage/brain.py#8 $ $Date: 2002/12/07 $

"""
An implementation of the three-state Brian's Brain rule.
"""

__package__ = 'cage'


import curses

import cage


class BrainAutomaton(cage.SynchronousAutomaton):
    states = 3
    QUIESCENT, FIRING, REFRACTORY = range(states)

    def __init__(self, size):
        cage.SynchronousAutomaton.__init__(self, cage.MooreMap(size))

    def rule(self, address):
        state = self.map.get(address)
        if state == BrainAutomaton.QUIESCENT:
            if self.map.countWith(address, BrainAutomaton.FIRING) == 2:
                return BrainAutomaton.FIRING
            else:
                return BrainAutomaton.QUIESCENT
        elif state == BrainAutomaton.FIRING:
            return BrainAutomaton.REFRACTORY
        elif state == BrainAutomaton.REFRACTORY:
            return BrainAutomaton.QUIESCENT
        else:
            assert 0, "unexpected state"


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = BrainAutomaton(player.size)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__':
    curses.wrapper(main)
