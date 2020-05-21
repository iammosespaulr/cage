#!/usr/local/bin/python
#
# $Id: //projects/cage/1d.py#14 $ $Date: 2002/12/07 $

"""
A trivial 1D automaton rule explorer.  The example used here is for
k = 2, r = 2, and the explorer displays a sample of the output for
each rule.  This would allow, for instance, classification of the
automata rules.
"""

__package__ = 'cage'


import cage


class TimedLinearCodedAutomaton(cage.LinearCodedAutomaton):
    def __init__(self, size, code):
        cage.LinearCodedAutomaton.__init__(self, size, code)

    def running(self):
        return self.generation < divmod(self.map.length, 2)[0]
        

def main():
    player = None
    total = 256
    for code in range(total):
        print "%d/%d" % (code, total)
        try:
            player = cage.LinePlayer(79)
            automaton = TimedLinearCodedAutomaton(player.size, code)
            cage.PointInitializer().initialize(automaton)
            player.main(automaton)
        finally:
            if player is not None:
                player.done()
            player = None
        print

if __name__ == '__main__': main()
