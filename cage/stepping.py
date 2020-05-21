#!/usr/local/bin/python
#
# $Id: //projects/cage/stepping.py#1 $ $Date: 2006/05/14 $

"""
An implementation of Packard's automaton.
"""

__package__ = 'cage'


import curses
import random
import sys

import cage


class SteppingStoneAutomaton(cage.SynchronousAutomaton):
    
    def __init__(self, size, states, threshold):
        cage.SynchronousAutomaton.__init__(self, cage.VonNeumannMap(size))
        self.states = states
        self.threshold = threshold
    
    def rule(self, address):
        if random.random() > self.threshold:
            return self.map.randomState(address)
        else:
            return self.map.get(address)


def main(stdscr):
    states = int(sys.argv[1])
    threshold = float(sys.argv[2])
    try:
        player = cage.CursesPlayer(stdscr)
        automaton = SteppingStoneAutomaton(player.size, states, threshold)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >> sys.stderr, "usage: %s <states> <threshold>" % sys.argv[0]
        sys.exit()
    curses.wrapper(main)
