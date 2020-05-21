#!/usr/bin/env python
#
# $Id: //projects/cage/cage.py#51 $ $Date: 2006/07/29 $

"""
A full-featured, generic cellular automata engine in Python.
"""

__program__ = 'cage'
__version__ = '1.1.4'
__url__ = 'http://www.alcyone.com/software/cage/'
__author__ = 'Erik Max Francis <max@alcyone.com>'
__copyright__ = 'Copyright (C) 2002-2006 Erik Max Francis'
__license__ = 'GPL'


import operator
import random
import types

try:
    import curses
except ImportError:
    curses = None

try:
    import Image
except ImportError:
    Image = None


#
# Topology
#

class Topology:
    
    """A topology is the encapsulation of the shape and dimensionality
    of a cellular network.  Note: Topologies and neighborhoods are
    used as mixins to create a map."""
    
    dimension = None
    background = 0
    
    def __init__(self, size):
        if self.__class__ is Topology:
            raise NotImplementedError
        assert len(size) == self.dimension
        self.size = size
        self.cells = reduce(operator.mul, self.size, 1)
        self.zero = (0,)*self.dimension

    def isNormalized(self, address):
        """Is the address already normalized?"""
        return address == self.normalize(address)

    def normalize(self, address):
        """Normalize an address (in the case of multiply-connected topologies,
        or None if the address cannot be normalized."""
        raise NotImplementedError

    def get(self, address):
        """Get the state of the cell at address."""
        raise NotImplementedError

    def set(self, address, state):
        """Set the state of the cell at addess."""
        raise NotImplementedError

    def reset(self, address):
        """Reset the state of the cell to the background."""
        self.set(address, self.background)

    def center(self):
        """A cell that's roughly in the center of the topology."""
        address = map(lambda x: divmod(x, 2)[0], self.size)
        return tuple(address)

    def random(self):
        """Create a random valid (normalized) address in this topology."""
        address = map(random.randrange, self.size)
        return tuple(address)

    def clone(self):
        """Make a morphologically identical copy (with perhaps a different
        cell configuration).  This is for CAs which need to manage multiple
        morphologically identical topologies, such as synchronous automata
        (the most common kind).  This should be overridden at the Map
        level."""
        raise NotImplementedError


class LineTopology(Topology):

    """A one-dimensional, bounded topology consisting of a line of
    cells arranged in a row."""
    
    dimension = 1
    border = 0

    def __init__(self, size):
        Topology.__init__(self, size)
        self.length, = size
        self.buffer = [self.background] * self.length

    def normalize(self, address):
        x, = address
        if x < 0 or x >= self.length:
            return None
        return address

    def get(self, address):
        result = self.normalize(address)
        if result is None:
            return self.border
        x, = result
        return self.buffer[x]

    def set(self, address, state):
        x, = address
        assert x >= 0 and x < self.length
        self.buffer[x] = state


class CircleTopology(LineTopology):

    """A one-dimensional, unbounded topology consisting of a line of
    cells turned back on itself; the 'leftmost' cell is adjacent to
    the 'rightmost' one."""
    
    dimension = 1

    def __init__(self, size):
        LineTopology.__init__(self, size)

    def normalize(self, address):
        x, = address
        if x < 0:
            x += self.length
        elif x >= self.length:
            x -= self.length
        return (x,)

    def get(self, address):
        x, = self.normalize(address)
        return self.buffer[x]


class GridTopology(Topology):

    """A two-dimensional, bounded topology consisting of a rectangular
    grid of cells."""
    
    dimension = 2
    border = 0
    
    def __init__(self, size):
        Topology.__init__(self, size)
        self.width, self.height = size
        self.buffer = []
        for x in range(self.width):
            self.buffer.append([self.background] * self.height)

    def normalize(self, address):
        x, y = address
        if (x < 0 or x >= self.width or 
            y < 0 or y >= self.height):
            return None
        return address

    def get(self, address):
        result = self.normalize(address)
        if result is None:
            return self.border
        x, y = result
        return self.buffer[x][y]
    
    def set(self, address, state):
        x, y = address
        assert (x >= 0 and x < self.width and 
                y >= 0 and y < self.height)
        self.buffer[x][y] = state


class ToroidTopology(GridTopology):

    """A two-dimensional, unbounded topology consisting of a
    rectangular grid of cells, where the 'northmost' row is adjacent
    to the 'southmost,' and the 'eastmost' column is adjacent to the
    'westmost.'"""
    
    dimension = 2
    
    def __init__(self, size):
        GridTopology.__init__(self, size)

    def normalize(self, address):
        x, y = address
        if x < 0:
            x += self.width
        elif x >= self.width:
            x -= self.width
        if y < 0:
            y += self.height
        elif y >= self.height:
            y -= self.height
        return x, y

    def get(self, address):
        x, y = self.normalize(address)
        return self.buffer[x][y]

#
# Neighborhood
#

class Neighborhood:

    """The abstraction of a neighbhorhood, or the set of cells that
    are 'adjacent' to any given cell.  Neighborhoods are not consider
    to be inclusive (containing the primary cell itself) since support
    methods support selecting between inclusive and exclusive
    neighborhoods.  Note: Topologies and neighborhoods are used as
    mixins to create a map."""
    
    def __init__(self):
        if self.__class__ is Neighborhood:
            raise NotImplementedError

    def neighborhood(self):
        """Return the number of neighbors in the neighborhood; this method
        should raise if the neighbor count varies."""
        raise NotImplementedError

    def neighbors(self, address):
        """Return a list of addresses which are neighbors.  This is the main
        entry point for determing neighborhoods."""
        raise NotImplementedError

    # Support functions for doing computations on neighborhoods; these need
    # not be overridden.

    def states(self, address):
        """Return the list of cell values for all neighbors."""
        return [self.get(x) for x in self.neighbors(address)]

    def inclusiveStates(self, address):
        """Return the list of cell values for all neighbors, including this
        (at the end)."""
        return self.states(address) + [self.get(address)]

    def sum(self, address):
        """Sum the states of the neighboring cells."""
        return reduce(operator.add, self.states(address))

    def inclusiveSum(self, address):
        """Sum the states of the neighboring cells as well as this one."""
        states = self.states(address)
        return reduce(operator.add, states) + self.get(address)

    def average(self, address):
        """The average of the neighbors' states."""
        return self.sum(address)/self.neighborhood()

    def inclusiveAverage(self, address):
        """The average of the neighbors' state, including this ones."""
        return self.inclusiveSum(address)/(self.neighborhood() + 1)

    def hasZero(self, address):
        """Do any neighbors have zero state?"""
        for neighbor in self.neighbors(address):
            if self.get(neighbor) == 0:
                return 1
        return 0

    def countZero(self, address):
        """Count the number of neighbors with state zero."""
        count = 0
        for neighbor in self.neighbors(address):
            if self.get(neighbor) == 0:
                count += 1
        return count

    def hasNonZero(self, address):
        """Do any neighbors have nonzero state?"""
        for neighbor in self.neighbors(address):
            if self.get(neighbor) != 0:
                return 1
        return 0

    def countNonZero(self, address):
        """Count the number of neighbors with state zero."""
        count = 0
        for neighbor in self.neighbors(address):
            if self.get(neighbor) != 0:
                count += 1
        return count

    def hasWith(self, address, state):
        """Do any neighbors have the given state?"""
        for neighbor in self.neighbors(address):
            if self.get(neighbor) == state:
                return 1
        return 0

    def countWith(self, address, state):
        """Count the number of neighbors with given state."""
        count = 0
        for neighbor in self.neighbors(address):
            if self.get(neighbor) == state:
                count += 1
        return count

    def findFirstWith(self, address, state):
        """Finds index (into neighbor list) of first neighbor with given
        state, or None."""
        neighbors = self.neighbors(address)
        for i in range(len(neighbors)):
            if self.get(neighbors[i]) == state:
                return i
        return None

    def findAllWith(self, address, state):
        """Return list of indexes of neighbors with the given state."""
        found = []
        neighbors = self.neighbors(address)
        for i in range(len(neighbors)):
            if self.get(neighbors[i]) == state:
                found.append(i)
        return found

    def randomState(self, address):
        """Return a random neighbor's state."""
        return self.get(random.choice(self.neighbors(address)))

    def reduce(self, address, func, initial=0):
        """Do an arbitrary reduction of the states."""
        return reduce(func, self.states(address), initial)


class NullNeighborhood(Neighborhood):

    """A null neighborhood, literally consisting of no neighbors
    whatsoever.  Useful for cases where agents are used to process
    automata, instead of a cellular network."""
    
    def __init__(self):
        Neighborhood.__init__(self)

    def neighborhood(self): return 0

    def neighbors(self, address): return []

    
class RadialNeighborhood(Neighborhood):

    """A one-dimensional neighborhood consisting of the cells to the
    left and right to a certain 'radius."""
    
    def __init__(self, radius):
        Neighborhood.__init__(self)
        self.radius = radius
                 
    def neighborhood(self): return 2*self.radius

    def neighbors(self, address):
        x, = address
        result = []
        for i in range(self.radius):
            result.append((x + i + 1,))
            result.append((x - i - 1,))
        return result


class VonNeumannNeighborhood(Neighborhood):

    """The von Neumann neighborhood.  A two-dimensional neighborhood
    consisting of the cells in the cardinal directions only."""
    
    def __init__(self):
        Neighborhood.__init__(self)
    
    def neighborhood(self): return 4
    
    def neighbors(self, address):
        x, y = address
        return [(x + 1, y), 
                (x,     y + 1), 
                (x - 1, y), 
                (x,     y - 1)]


class MooreNeighborhood(Neighborhood):

    """The Moore neighborhood.  A two-dimensional neighborhood
    consisting of the cells in all eight cardinal and ordinal
    directions."""
    
    def __init__(self):
        Neighborhood.__init__(self)
    
    def neighborhood(self): return 8
    
    def neighbors(self, address):
        x, y = address
        return [(x + 1, y), 
                (x + 1, y + 1), 
                (x,     y + 1), 
                (x - 1, y + 1), 
                (x - 1, y), 
                (x - 1, y - 1), 
                (x,     y - 1), 
                (x + 1, y - 1)]
    
class HexagonalNeighborhood(Neighborhood):

    """A two-dimensional, hexagonally-shaped neighborhood."""
    
    def __init__(self):
        Neighborhood.__init__(self)
    
    def neighborhood(self): return 6
    
    def neighbors(self, address):
        x, y = address
        return [(x + 1, y), 
                (x + 1, y + 1), 
                (x,     y + 1), 
                (x - 1, y - 1), 
                (x,     y - 1), 
                (x + 1, y - 1)]


class KnightsNeighborhood(Neighborhood):

    """A two-dimensional neighborhood encompassing all the legal moves
    of a knight in chess."""
    
    def __init__(self):
        Neighborhood.__init__(self)
    
    def neighborhood(self): return 8
    
    def neighbors(self, address):
        x, y = address
        return [(x + 1, y + 2), 
                (x + 2, y + 1), 
                (x + 2, y - 1), 
                (x + 1, y - 2), 
                (x - 1, y - 2), 
                (x - 2, y - 1), 
                (x - 2, y + 1), 
                (x - 1, y + 2)]


#
# Map (Topology + Neighborhood mixing)
#

class LineMap(LineTopology, RadialNeighborhood):

    """A standard one-dimensional, line map."""
    
    def __init__(self, size, radius):
        LineTopology.__init__(self, size)
        RadialNeighborhood.__init__(self, radius)

    def clone(self):
        return LineMap(self.size, self.radius)


class RadialMap(CircleTopology, RadialNeighborhood):

    """A standard one-dimensional, radial map."""
    
    def __init__(self, size, radius):
        CircleTopology.__init__(self, size)
        RadialNeighborhood.__init__(self, radius)

    def clone(self):
        return RadialMap(self.size, self.radius)


class VonNeumannMap(ToroidTopology, VonNeumannNeighborhood):

    """A standard two-dimensional, von Neumann map."""
    
    def __init__(self, size):
        ToroidTopology.__init__(self, size)
        VonNeumannNeighborhood.__init__(self)

    def clone(self):
        return VonNeumannMap(self.size)


class MooreMap(ToroidTopology, MooreNeighborhood):
    
    """A standard two-dimensional, Moore map."""
    
    def __init__(self, size):
        ToroidTopology.__init__(self, size)
        MooreNeighborhood.__init__(self)

    def clone(self):
        return MooreMap(self.size)


class KnightsMap(ToroidTopology, KnightsNeighborhood):
    
    """A standard two-dimensional, knight's neighborhood map."""
    
    def __init__(self, size):
        ToroidTopology.__init__(self, size)
        KnightsNeighborhood.__init__(self)

    def clone(self):
        return KnightsMap(self.size)



#
# Direction
#

class Direction:

    """A generalized direction on a 2-dimensional topology.  For use
    with agents which navigate their way around a topology without
    respect to neighborhoods."""
    
    DIRECTIONS = None # the number of valid directions
    OFFSETS = None
    ICONS = None

    def __init__(self, facing=0):
        assert self.DIRECTIONS is not None
        assert self.OFFSETS is not None
        assert self.ICONS is not None
        self.facing = facing

    def turn(self, increment):
        """Changing the facing by an integer (positive or negative)."""
        self.facing += increment
        if self.facing < 0 or self.facing >= self.DIRECTIONS:
            self.facing %= self.DIRECTIONS

    def turnLeft(self): self.turn(+1)
    def turnRight(self): self.turn(-1)

    def offset(self):
        """Return the offset for the current facing."""
        return self.OFFSETS[self.facing]

    def advance(self, location):
        """Given a location, use the direction to determine where the
        new location would be after advancing and return that."""
        offset = self.offset()
        newLocation = location[0] + offset[0], location[1] + offset[1]
        return newLocation


class CardinalDirection(Direction):

    """A cardinal direction: one of the four primary compass points."""
    
    OFFSETS = [(1, 0), (0, -1), (-1, 0), (0, 1)]
    DIRECTIONS = len(OFFSETS)
    ICONS = '-|-|'

    EAST, NORTH, SOUTH, WEST = range(DIRECTIONS)

    
class OrdinalDirection(Direction):

    """A cardinal or ordinal direction: any of the eight compass points."""
    
    OFFSETS = [(1, 0), (1, -1), (0, -1), (-1, -1), 
               (-1, 0), (-1, 1), (0, 1), (1, 1)]
    DIRECTIONS = len(OFFSETS)
    ICONS = "-/|\\-/|\\"

    (EAST, NORTHEAST, NORTH, NORTHWEST, 
     WEST, SOUTHWEST, SOUTH, SOUTHEAST) = range(DIRECTIONS)


class HexagonalDirection(Direction):

    """An hexagonal direction, analogous to hexagonal neighborhoods."""
    
    OFFSETS = [(1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1)]
    DIRECTIONS = len(OFFSETS)
    ICONS = "-/\\-/\\"

    EAST, NORTHEAST, NORTHWEST, WEST, SOUTHWEST, SOUTHEAST = range(DIRECTIONS)



#
# Agent
#

class Agent:

    """An agent is an arbitrary object that can roam around on a map,
    independent of the underlying automata."""
    
    def __init__(self, automaton, location=None):
        if self.__class__ is Agent:
            raise NotImplementedError
        self.automaton = automaton
        if location is None:
            location = self.automaton.map.zero
        self.location = location

    def update(self):
        raise NotImplementedError

    def between(self):
        pass


#
# Rule
#

class Rule:

    """The rule is an optional mixin class (intended to be mixed in
    with an Automaton) which allows implementation of generic rules
    without reference to dimensionality, topology, neighborhood, or
    any combination.  Rules, when used, include a populate method, and
    a rule method; the rule method is the same Automaton.rule method
    (which implements state transitions); the populate method is
    called once when the automaton is initialized and can, say,
    initialize lookup tables that the rule method relies upon."""

    def __init__(self):
        if self.__class__ is Rule:
            raise NotImplementedError

    def populate(self):
        """Initialize information needed to calculate rules, e.g., a
        lookup table."""
        pass

    def rule(self, address):
        """The main state transition function, prepackaged as a Rule."""
        raise NotImplementedError


class ReductionRule:

    """A reduction rule takes the list of states and reduces them
    against a given function."""

    def __init__(self, function):
        self.function = function

    def rule(self, address):
        return reduce(self.function, self.map.states(address))


class CodedTotalisticRule:

    """A two-state totalistic rule, expressed in terms of two sets (a
    2-tuple): the set of totals that will result in a dead cell
    becoming alive, and the set of totals that will result in a live
    cell remaining alive; all other totals will result in a cell
    becoming or remaining dead.  Also included is the standard
    notation including the list as numbers separated by a slash; e.g.,
    the rule for Conway's Game of Life would be 3/23."""

    def __init__(self, ruleCode):
        if type(ruleCode) is types.StringType:
            ruleCode = self.parseRule(ruleCode)
        self.populate(ruleCode)

    def parseRule(self, ruleString):
        """Translate a string into a rule code."""
        bornSums, staySums = [], []
        bornString, stayString = ruleString.split('/')
        if bornString[0] in 'Bb':
            bornString = bornString[1:]
        for c in bornString:
            n = ord(c) - ord('0')
            bornSums.append(n)
        if stayString[0] in 'Ss':
            stayString = stayString[1:]
        for c in stayString:
            n = ord(c) - ord('0')
            staySums.append(n)
        return bornSums, staySums

    def clear(self):
        """Create and clear the table."""
        neighborhood = self.map.neighborhood()
        assert neighborhood is not None
        self.table = []
        for i in range(self.states):
            self.table.append([0] * (neighborhood + 1))

    def populate(self, ruleCode):
        """Populate the table."""
        bornSums, staySums = ruleCode
        self.clear()
        for born in bornSums:
            self.table[0][born] = 1
        for stay in staySums:
            self.table[1][stay] = 1

    def rule(self, address):
        return self.table[self.map.get(address)][self.map.sum(address)]


class LinearCodedRule(Rule):

    """A linear coded rule is one which enumerates all possible rules.
    In this case only two-state 1D automata with a radius of 1 are
    supported."""

    def __init__(self, code):
        Rule.__init__(self)
        self.populate(code)
    
    def clear(self):
        self.table = [[[0]*2 for i in range(2)] for j in range(2)]

    def populate(self, code):
        self.clear()
        i = 0
        for right in range(2):
            for this in range(2):
                for left in range(2):
                    if code & (1 << i):
                        value = 1
                    else:
                        value = 0
                    self.table[left][this][right] = value
                    i += 1
        assert i == 8

    def rule(self, address):
        left, right, this = self.map.inclusiveStates(address)
        return self.table[left][this][right]



#
# Automaton
#

class Automaton:

    """An automaton joins together the map, the number of possible
    states (held in the states attribute, a rule for the transition of
    one cell state to another at a new time step, and manages a
    (possibly empty) collection of agents that can move around
    independently of the cellular network."""
    
    states = None
    
    def __init__(self, map):
        if self.__class__ is Automaton:
            raise NotImplementedError
        self.map = map
        self.generation = 0
        self.agents = []

    def running(self):
        """Is the automaton still running?"""
        return 1

    def update(self):
        """Update the automaton one time step."""
        self.generation += 1
        for agent in self.agents:
            agent.update()
    
    def between(self):
        """Hook to do things between generations."""
        for agent in self.agents:
            agent.between()

    def add(self, agent):
        """Add an agent."""
        assert agent not in self.agents
        self.agents.append(agent)

    def remove(self, agent):
        """Remove an agent."""
        assert agent in self.agents
        self.agents.remove(agent)

    # The rule function should be implemented here, but isn't so that mixin
    # Rule subclasses can be included without having to explicitly define
    # a rule method that calls a Rule.rule method.  The rule method should
    # have this signature:
    #
    #     def rule(self, address): ...


class AgentAutomaton(Automaton):

    """An automaton intended only for use by agents; no underlying
    cellular automaton will be operating."""

    def __init__(self, map):
        Automaton.__init__(self, map)

    def rule(self, address): pass


class AsynchronousAutomaton(Automaton):

    """An asynchronous automaton uses one map and updates each cell in
    unspecified order.  The state transitions of each cell will be
    sensitive to those that have been made before it in this update,
    so is generally unsuitable for automata work where all transitions
    should be simultaneous."""
    
    def __init__(self, map):
        Automaton.__init__(self, map)

    def update(self):
        ### This should be generalized instead of going case by case.
        if self.map.dimension == 1:
            for x in range(self.map.length):
                address = (x,)
                newCell = self.rule(address)
                self.map.set(address, newCell)
        elif self.map.dimension == 2:
            for x in range(self.map.width):
                for y in range(self.map.height):
                    address = x, y
                    newCell = self.rule(address)
                    self.map.set(address, newCell)
        else:
            raise NotImplementedError, "unsupported map dimensionality"
        Automaton.update(self)
        

class SynchronousAutomaton(Automaton):

    """A synchronous automaton updates all cells simultaneously (that
    is, during a given update, no state transition will affect the
    transition of any other cell).  This is probably the automaton you
    want to start from."""
    
    def __init__(self, map):
        Automaton.__init__(self, map)
        self.workMap = map.clone()

    def update(self):
        ### This should be generalized instead of going case by case.
        if self.map.dimension == 1:
            for x in range(self.map.length):
                address = (x,)
                newCell = self.rule(address)
                self.workMap.set(address, newCell)
        elif self.map.dimension == 2:
            for x in range(self.map.width):
                for y in range(self.map.height):
                    address = x, y
                    newCell = self.rule(address)
                    self.workMap.set(address, newCell)
        else:
            raise NotImplementedError, "unsupported map dimensionality"
        self.swap()
        Automaton.update(self)

    def swap(self):
        self.map.buffer, self.workMap.buffer = \
                         self.workMap.buffer, self.map.buffer


class TwoStateAutomaton(SynchronousAutomaton):

    """A two-state automaton is a synchronous automaton that has, not
    surprisingly, only two possible states.  They are typically
    referred to as dead and alive."""
    
    states = 2
    DEAD, ALIVE = range(states)


class TwoStateReductionAutomaton(TwoStateAutomaton, ReductionRule):

    """A two-state, synchronous automaton with a reduction rule."""
    
    def __init__(self, map, function):
        TwoStateAutomaton.__init__(self, map)
        ReductionRule.__init__(self, function)


class TwoStateTotalisticAutomaton(TwoStateAutomaton, CodedTotalisticRule):

    """A two-state, synchronous automaton with a Moore map and the
    binary totalistic rule."""
    
    def __init__(self, map, ruleCode):
        TwoStateAutomaton.__init__(self, map)
        CodedTotalisticRule.__init__(self, ruleCode)


class ConwayAutomaton(TwoStateTotalisticAutomaton):

    """Conway's Game of Life, with an optional flag for 'high life.'"""

    def __init__(self, size, highLife=0):
        if highLife:
            code = [3, 6], [2, 3]
        else:
            code = [3], [2, 3]
        TwoStateTotalisticAutomaton.__init__(self, MooreMap(size), code)


class LinearCodedAutomaton(TwoStateAutomaton, LinearCodedRule):

    """A two-state, synchronous automaton with a linear coded rule
    (r = 1, k = 1)."""

    def __init__(self, size, code):
        TwoStateAutomaton.__init__(self, LineMap(size, 1))
        LinearCodedRule.__init__(self, code)



#
# Initializer
#

class Initializer:

    """An initializer simply sets up the contents of a network before
    processing begins."""
    
    def __init__(self):
        if self.__class__ is Initializer:
            raise NotImplementedError
    
    def initialize(self, automaton):
        raise NotImplementedError


class PointInitializer(Initializer):

    """A point initializer starts with an initially blank grid and
    sets exactly one cell to the specified state."""

    def __init__(self, address=None, state=1):
        Initializer.__init__(self)
        self.address = address
        self.state = state

    def initialize(self, automaton):
        map = automaton.map
        address = self.address
        if address is None:
            address = map.center()
        map.set(address, self.state)
        

class RandomInitializer(Initializer):

    """A random initializer sets all the cells in the network to some
    random non-zero value with the specified frequency."""
    
    def __init__(self, frequency=None):
        Initializer.__init__(self)
        self.frequency = frequency

    def initialize(self, automaton):
        states = automaton.states
        frequency = self.frequency
        if frequency is None:
            frequency = (states - 1.0)/states
        ### This should be generalized instead of going case by case.
        map = automaton.map
        if map.dimension == 1:
            for x in range(map.length):
                if random.random() < frequency:
                        map.set((x,), 
                                random.randrange(automaton.states - 1) + 1)
        elif map.dimension == 2:
            for x in range(map.width):
                for y in range(map.height):
                    if random.random() < frequency:
                        map.set((x, y), 
                                random.randrange(automaton.states - 1) + 1)
        else:
            raise NotImplementedError, "unsupported map dimensionality"


class SeedInitializer(Initializer):

    """A seed initializer places count cells of the specific state in
    random positions on the network."""
    
    def __init__(self, count, state=1):
        Initializer.__init__(self)
        self.count = count
        self.state = state

    def initialize(self, automaton):
        map = automaton.map
        assert self.count < map.cells
        seeds = []
        for i in range(self.count):
            while 1:
                address = map.random()
                if address in seeds:
                    continue
                map.set(address, self.state)
                break
            seeds.append(address)


class PatternInitializer(Initializer):

    """A pattern initializer takes a (two-dimensional) pattern and
    grafts it ont to the network roughly in the center of the
    topology."""
    
    def __init__(self, pattern):
        Initializer.__init__(self)
        self.pattern = pattern
        self.width = 0
        self.height = len(self.pattern)
        for y in range(self.height):
            if len(self.pattern[y]) > self.width:
                self.width = len(self.pattern[y])

    def initialize(self, automaton):
        map = automaton.map
        ### Hardcoded to only implement patterns which are sequences of
        ### sequences of lists.
        assert map.dimension == 2
        assert self.width <= map.width and self.height <= map.height
        left = divmod(map.width - self.width, 2)[0]
        bottom = divmod(map.height - self.height, 2)[0]
        for y in range(self.height):
            for x in range(len(self.pattern[y])):
                map.set((left + x, bottom + y), self.pattern[y][x])


class StringInitializer(PatternInitializer):

    """A pattern initializer that takes a list of ASCII strings
    representing the pattern rather than a list of list of cell
    states."""

    def __init__(self, stringPattern):
        pattern = []
        ### Similar to PatternInitializer, but sequences of sequences of
        ### chars (typically sequences of strings).
        for stringLine in stringPattern:
            line = map(int, stringLine)
            pattern.append(line)
        PatternInitializer.__init__(self, pattern)



#
# Player
#

class Player:

    """Players simple orchestrate the running of an automaton and
    present a user interface."""
    
    def __init__(self):
        self.isRunning = 1
        self.automaton = None

    def __del__(self):
        self.done()

    def prelim(self):
        """Do any preliminary initialization after the Automaton has
        been attached."""
        pass
        
    def main(self, automaton=None):
        """The main event loop."""
        self.automaton = automaton
        self.prelim()

    def done(self):
        """Cleanup."""
        pass


class TextPlayer(Player):

    """Core routines for text-related players."""

    DIRECTIONS = {(1, 0): '-', (1, -1): '/', (0, -1): '|', (-1, -1): '\\', 
                  (-1, 0): '-', (-1, 1): '/', (0, 1): '|', (1, 1): '\\'}

    STATE_ICON_SPECTRUM = ' 123456789abcdefghijklmonpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    STATE_ICON_TABLES = (' #',
                         ' +#',
                         ' .+#',
                         ' .:+#',
                         ' .:+%#',
                         ' 123456789abcdefghijklmonpqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`~!@#$%^&*()-_=+[{]}\\|;:\'",<.>/?')

    def __init__(self):
        Player.__init__(self)
        if self.__class__ is TextPlayer:
            raise NotImplementedError
        self.stateIconTable = None
        self.states = None

    def stateIcon(self, state): return self.stateIconTable[state]

    def stateIconN(self, state):
        return self.STATE_ICON_SPECTRUM[int(26.*state/self.states)]

    def prelim(self):
        # Select the appropriate icon selection member based on the number
        # of states.
        self.states = self.automaton.states
        for iconTable in self.STATE_ICON_TABLES:
            if self.states <= len(iconTable):
                self.stateIconTable = iconTable
                break
        else:
            self.stateIcon = self.stateIconN

    def directionIcon(self, direction):
        ### Only works with two-dimensional maps.
        assert self.automaton.map.dimension == 2
        return self.DIRECTIONS[direction]


class LinePlayer(TextPlayer):

    """A line player displays a one-dimensional automaton with one row
    per line to stdout."""
    
    def __init__(self, length):
        TextPlayer.__init__(self)
        self.length = length
        self.size = (self.length,)
        self.inited = 1
        
    def display(self):
        map = self.automaton.map
        s = ''
        for x in range(map.length):
            s += self.stateIcon(map.get((x,)))
        print s

    def main(self, automaton):
        Player.main(self, automaton)
        assert self.automaton is not None
        assert self.automaton.map.dimension == 1 ###
        isRunning = 1
        self.display()
        while self.automaton.running():
            if isRunning:
                self.automaton.update()
                self.automaton.between()
                self.display()
                if isRunning < 0:
                    isRunning += 1


class CursesPlayer(TextPlayer):

    """A curses player displays a two-dimensional automaton with some
    simple controls (escape to quit, space to toggle running, enter to
    single step)."""
    
    def __init__(self, stdscr):
        assert curses
        TextPlayer.__init__(self)
        self.stdscr = stdscr
        curses.noecho()
        self.stdscr.nodelay(1)
        self.width = curses.COLS
        self.height = curses.LINES - 1
        self.size = self.width, self.height
        self.inited = 1

    def status(self):
        self.stdscr.addstr(curses.LINES - 1, 0, \
                           "t = %d" % self.automaton.generation)

    def display(self):
        map = self.automaton.map
        self.stdscr.erase()
        for x in range(map.width):
            for y in range(map.height):
                state = map.get((x, y))
                if state:
                    self.stdscr.addch(y, x, self.stateIcon(state))
        for agent in self.automaton.agents:
            # Show the agent in reverse video.
            icon = self.stateIcon(map.get(agent.location))
            ax, ay = agent.location
            self.stdscr.addch(ay, ax, icon, curses.A_REVERSE | curses.A_BOLD)
            if hasattr(agent, 'direction'):
                markLocation = agent.direction.advance(agent.location)
                if map.isNormalized(markLocation):
                    mx, my = markLocation
                    self.stdscr.addch(my, mx, \
                                      self.directionIcon(agent.direction.offset()), \
                                      curses.A_BOLD)
        self.status()
        self.stdscr.refresh()

    def main(self, automaton):
        Player.main(self, automaton)
        assert self.automaton is not None
        assert self.automaton.map.dimension == 2 ###
        curses.noecho()
        self.stdscr.nodelay(1)
        isRunning = 1
        self.display()
        while self.automaton.running():
            # Workaround to avoid using .getkey, since it results in segfaults
            # under some circumstances.
            charOrd = self.stdscr.getch()
            if charOrd >= 0:
                char = chr(charOrd)
            else:
                char = None
            if char == ' ':
                isRunning = not isRunning
            elif char in ('\r', '\n'):
                isRunning = -1
            elif char in ('1', '2', '3', '4', '5', '6', '7', '8', '9'):
                isRunning = -((ord(char) - ord('0'))*10)
            elif char == '0':
                isRunning = -100
            elif char in ('q', 'Q', '\x1b'):
                return
            if isRunning:
                self.automaton.update()
                self.automaton.between()
                self.display()
                if isRunning < 0:
                    isRunning += 1

    def done(self):
        if self.inited:
            self.inited = 0


class ImagePlayer(Player):
    def __init__(self, width, height):
        assert Image
        Player.__init__(self)
        self.width = width
        self.height = height
        self.image = Image.new('1', (width, height), 0)
        self.size = (width,)
        self.row = 0
        self.inited = 0

    def display(self):
        map = self.automaton.map
        for x in range(map.length):
            self.image.putpixel((x, self.row), 255*map.get((x,)))
        self.row += 1

    def main(self, automaton):
        Player.main(self, automaton)
        assert self.automaton is not None
        assert self.automaton.map.dimension == 1 ###
        while self.row < self.height and self.automaton.running():
            self.display()
            self.automaton.update()
            self.automaton.between()
        self.finish()

    def finish(self):
        self.image.show()
