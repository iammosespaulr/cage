#!/usr/local/bin/python
#
# $Id: //projects/cage/ant.py#10 $ $Date: 2006/05/14 $

"""
A sample implementation of a unique finite state automaton with agents.

The FSAs consist of *ants*, which are agents that move around on a
two-dimensional automaton.  Ants have a state, a location, and a
direction.  They also have two figures that determine how complex they
are: the total number of possible states they can have, and the total
number of colors that the ant can discern and manipulate; both of
these figures must powers of two.  Ants are deterministic creatures,
whose behavior is deterministically determined by their *genomes*;
these consists of three lookup tables, or *genes*: one for state, one
for color, and one for action.

Here, *color* refers to the cellular states of the underlying
automaton (which do not spontaneously change).  The total number of
colors that an ant can interact with acts as a bitmask, called the
*color mask*, on the underlying cell state; if an ant only can
interact with 8 colors, then it can only retrieve and change the lower
3 bits of the state of each cell it is located on.  The ant's *state*
is an internal designation that modifies its behavior; the state is an
integer between 0 and *N* - 1, where *N* is the total number of
states.  The lookup tables, or genes, are each used by the current
perceived color and state, and thus are two dimensional arrays.

Ants can also perform an *action*, which is one of the four possible
behaviors: do nothing, turn left, turn right, or move forward
(advance).

Each update, an ant will do the following:

- retrieve the cellular state and turn it into a color according to
  its color mask;
      
- use that color and the ant's current state to do lookups on each of
  the ant's genes to get its new state, new color, and action;

- apply the new color to the current cell state (taking into account
  the color mask);

- change to the new state;

- and, finally, perform the specified action.
"""

__package__ = 'cage'


import curses

import cage
import random
import sys


class Gene:
    
    """A single lookup table, mapping color and state to a value."""
    
    def __init__(self, colors, states):
        self.colors = colors
        self.states = states
        self.data = []
        for color in range(colors):
            self.data.append([0] * states)

    def get(self, color, state):
        assert 0 <= color < self.colors
        assert 0 <= state < self.states
        return self.data[color][state]

    def set(self, color, state, value):
        assert 0 <= color < self.colors
        assert 0 <= state < self.states
        self.data[color][state] = value

    def randomize(self, values):
        for color in range(self.colors):
            for state in range(self.states):
                self.set(color, state, random.randrange(values))

        
class Genome:

    """The encapsulation of the total number of states and colors, as
    well as the three "genes" -- color, state, and action."""
    
    ACTIONS = 4
    NONE, LEFT, RIGHT, ADVANCE = range(ACTIONS)
    
    def __init__(self, colors, states):
        assert colors & (colors - 1) == 0
        assert states & (states - 1) == 0
        self.colors = colors
        self.states = states
        self.color = Gene(colors, states)
        self.state = Gene(colors, states)
        self.action = Gene(colors, states)

    def randomize(self):
        self.color.randomize(self.colors)
        self.state.randomize(self.states)
        self.action.randomize(Genome.ACTIONS)


class Ant(cage.Agent):
    
    """An individual FSA in the system."""
    
    def __init__(self, automaton, genome, \
                 location = (0, 0), direction = 0, state = 0):
        cage.Agent.__init__(self, automaton, location)
        self.genome = genome
        self.direction = cage.OrdinalDirection(direction)
        self.state = state
        self.colorMask = self.genome.colors - 1

    def normalize(self):
        self.location = self.automaton.map.normalize(self.location)

    def advance(self):
        self.location = self.direction.advance(self.location)
        self.normalize()

    def update(self):
        map = self.automaton.map
        # Get the cell state and turn it into a color.
        cell = map.get(self.location)
        color = cell & self.colorMask
        # Do the genome lookups.
        newColor = self.genome.color.get(color, self.state)
        newState = self.genome.state.get(color, self.state)
        action = self.genome.action.get(color, self.state)
        # Update the cell it's standing on.
        assert 0 <= newColor < self.genome.colors
        newCell = (cell & ~self.colorMask) | newColor
        map.set(self.location, newCell)
        # Update the state.
        assert 0 <= newState < self.genome.states
        self.state = newState
        # Perform the action.
        if action == Genome.NONE:
            pass
        elif action == Genome.LEFT:
            self.direction.turnLeft()
        elif action == Genome.RIGHT:
            self.direction.turnRight()
        elif action == Genome.ADVANCE:
            self.advance()
        else:
            assert 0, "unknown action"


class Map(cage.ToroidTopology, cage.NullNeighborhood):
    
    """A standard toroidal topology with no neighborhood."""
    
    def __init__(self, size):
        cage.ToroidTopology.__init__(self, size)
        cage.NullNeighborhood.__init__(self)


class Automaton(cage.AgentAutomaton):
    
    """The actual automaton class."""
    
    states = None
    
    def __init__(self, size):
        cage.AgentAutomaton.__init__(self, Map(size))
        

def main(stdscr):
    ants, colors, states = map(int, sys.argv[1:])
    try:
        player = cage.CursesPlayer(stdscr)
        size = player.size
        automaton = Automaton(size)
        automaton.states = colors
        center = automaton.map.center()
        for i in range(ants):
            genome = Genome(colors, states)
            genome.randomize()
            automaton.add(Ant(automaton, genome, center))
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print >> sys.stderr, "usage: %s <ants> <colors> <states>" % sys.argv[0]
        sys.exit()
    curses.wrapper(main)
