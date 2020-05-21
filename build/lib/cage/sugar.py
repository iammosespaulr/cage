#!/usr/local/bin/python
#
# $Id: //projects/cage/sugar.py#9 $ $Date: 2002/12/07 $

"""
An implementation of the Belousov-Zhabotinsky reaction.  *Note:*  This
automaton takes a fair bit of time to get going to see the full effect.
"""

__package__ = 'cage'


import curses

import cage


class SugarAutomaton(cage.SynchronousAutomaton):
    states = 100
    HEALTHY, SICK = 0, 99

    def __init__(self, size):
        cage.SynchronousAutomaton.__init__(self, cage.MooreMap(size))

    def rule(self, address):
        state = self.map.get(address)
        isUnhealthy = state != self.HEALTHY
        if state == self.HEALTHY:
            return divmod(self.map.countNonZero(address) + isUnhealthy, 2)[0] \
                   + divmod(self.map.countWith(address, self.SICK), 3)[0]
        elif state == self.SICK:
            return self.HEALTHY
        else:
            newState = self.map.inclusiveSum(address)/\
                       (self.map.countNonZero(address) + isUnhealthy) + 15
            if newState >= self.states:
                newState = self.SICK
            return newState


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = SugarAutomaton(player.size)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
