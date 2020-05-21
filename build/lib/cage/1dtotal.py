#!/usr/local/bin/python
#
# $Id: //projects/cage/1dtotal.py#7 $ $Date: 2002/12/07 $

"""
A trivial 1D automaton rule explorer.  The example used here is for
k = 2, r = 2, and the explorer displays a sample of the output for
each rule.  This would allow, for instance, classification of the
automata rules.
"""

__package__ = 'cage'


import cage


class LinearTotalisticAutomaton(cage.SynchronousAutomaton):
    def __init__(self, size, k, r, code):
        cage.SynchronousAutomaton.__init__(self, cage.LineMap(size, r))
        self.states = k
        self.table = []
        self.populate(code)

    def running(self):
        return self.generation < divmod(self.map.length, 2)[0]

    def populate(self, code):
        sums = (2*self.map.radius + 1) + 1
        for i in range(sums):
            if code & (1 << i):
                self.table.append(1)
            else:
                self.table.append(0)

    def rule(self, address):
        return self.table[self.map.inclusiveSum(address)]


def main():
    player = None
    k = 2
    r = 2
    total = 2*k**(2*r + 1)
    for code in range(0, total + 1, 2):
        print "%d/%d" % (code, total)
        try:
            player = cage.LinePlayer(79)
            automaton = LinearTotalisticAutomaton(player.size, k, r, code)
            cage.RandomInitializer().initialize(automaton)
            player.main(automaton)
        finally:
            if player is not None:
                player.done()
        print

if __name__ == '__main__': main()
