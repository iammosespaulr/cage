#!/usr/local/bin/python

"""
A simulation of a chain reaction.
"""

import random
import curses

import cage


FIRE_PROBABILITY = 0.8
PARTICLES = 2
RADIUS = 2


class Map(cage.ToroidTopology, cage.NullNeighborhood):

    """A standard toroidal topology."""

    def __init__(self, size):
        cage.ToroidTopology.__init__(self, size)
        cage.NullNeighborhood.__init__(self)


class Automaton(cage.AsynchronousAutomaton):
    
    """The actual automaton class.  Maintain the list of chain reacting
    particles as a list."""

    states = 3
    CHARGED, FIRING, FIRED = range(states)
    
    def __init__(self, size):
        cage.AsynchronousAutomaton.__init__(self, Map(size))
        self.particles = []

    def rule(self, address):
        state = self.map.get(address)
        if state == Automaton.FIRING:
            self.fire(address)
            return Automaton.FIRED
        return state

    def fire(self, address):
        if random.random() < FIRE_PROBABILITY:
            for i in range(PARTICLES):
                while 1:
                    dx = random.randrange(2*RADIUS + 1) - RADIUS
                    dy = random.randrange(2*RADIUS + 1) - RADIUS
                    if (dx, dy) != (0, 0):
                        break
                x, y = address
                x += dx
                y += dy
                self.particles.append((x, y))

    def between(self):
        for address in self.particles:
            address = self.map.normalize(address)
            if self.map.get(address) == Automaton.CHARGED:
                self.map.set(address, Automaton.FIRING)
        self.particles[:] = []


def main(stdscr):
    try:
        player = cage.CursesPlayer(stdscr)
        size = player.size
        automaton = Automaton(size)
        cage.PointInitializer(state=Automaton.FIRING).initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__': curses.wrapper(main)
