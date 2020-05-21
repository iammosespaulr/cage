#!/usr/local/bin/python
#
# $Id: //projects/cage/vant.py#12 $ $Date: 2006/05/14 $

"""
An implementation of Langton's virtual ants (vants).
"""

__package__ = 'cage'


import curses

import cage


class Vant(cage.Agent):
    
    DIRECTIONS = 4
    LEFT, RIGHT = -1, +1
    
    def __init__(self, automaton, location=None, direction=0):
        cage.Agent.__init__(self, automaton, location)
        self.direction = cage.CardinalDirection(direction)

    def normalize(self):
        self.location = self.automaton.map.normalize(self.location)

    def advance(self):
        self.location = self.direction.advance(self.location)
        self.normalize()

    def update(self):
        map = self.automaton.map
        state = map.get(self.location)
        if state:
            self.direction.turnRight()
        else:
            self.direction.turnLeft()
        map.set(self.location, not state)
        self.advance()


class Map(cage.ToroidTopology, cage.NullNeighborhood):
    
    def __init__(self, size):
        cage.ToroidTopology.__init__(self, size)
        cage.NullNeighborhood.__init__(self)

    def clone(self): assert 0 # Automaton is not synchronous, so not needed.
        

class Automaton(cage.AgentAutomaton):
    
    states = 2
    
    def __init__(self, size):
        cage.AgentAutomaton.__init__(self, Map(size))


def main(stdscr):
    import sys
    if len(sys.argv) < 2:
        vants = 1
    else:
        vants = int(sys.argv[1])
    try:
        player = cage.CursesPlayer(stdscr)
        size = player.size
        automaton = Automaton(size)
        map = automaton.map
        for i in range(vants):
            if i == 0:
                loc = map.center()
            else:
                loc = map.random()
            automaton.add(Vant(automaton, loc))
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__':
    curses.wrapper(main)
