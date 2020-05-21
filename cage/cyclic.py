#!/usr/local/bin/python
#
# $Id: //projects/cage/cyclic.py#8 $ Date$

"""
An implementation of the Demons of Cycling Space automaton.  *Note:*
This automaton usually requires a fairly large map to get going in its
full glory.
"""

__package__ = 'cage'


import curses

import cage


class CyclicAutomaton(cage.SynchronousAutomaton):
    states = 7 ###
    assert states <= 26
    
    def __init__(self, size):
        cage.SynchronousAutomaton.__init__(self, cage.VonNeumannMap(size))
    
    def rule(self, address):
        state = self.map.get(address)
        statePlusOne = state + 1
        if statePlusOne == self.states:
            statePlusOne = 0
        if self.map.hasWith(address, statePlusOne):
            return statePlusOne
        else:
            return state


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = CyclicAutomaton(player.size)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
