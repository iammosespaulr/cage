#!/usr/local/bin/python
#
# $Id: //projects/cage/vote.py#12 $ $Date: 2006/05/15 $

"""
An implementating of the voting rule.
"""

__package__ = 'cage'


import curses

import cage


class VoteAutomaton(cage.SynchronousAutomaton):
    
    states = 2
    DEAD, ALIVE = range(states)

    normalTable = [DEAD, DEAD, DEAD, DEAD, DEAD, 
                   ALIVE, ALIVE, ALIVE, ALIVE, ALIVE]
    twistTable = [DEAD, DEAD, DEAD, DEAD, ALIVE, 
                  DEAD, ALIVE, ALIVE, ALIVE, ALIVE]

    def __init__(self, size, twist=True):
        cage.SynchronousAutomaton.__init__(self, cage.MooreMap(size))
        if twist:
            self.table = self.twistTable
        else:
            self.table = self.normalTable

    def rule(self, address):
        return self.table[self.map.inclusiveSum(address)]


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = VoteAutomaton(player.size)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
