#!/usr/local/bin/python
#
# $Id: //projects/cage/total.py#6 $ $Date: 2002/12/07 $

"""
An implementation of arbitrary two-state totalistic automata.
"""

__package__ = 'cage'


import curses

import cage
import sys


RULES = {'conway': '3/23',
         'highlife': '36/23',
         'diamoeba': '35678/5678'}


def main(stdscr):
    global RULES
    rule = sys.argv[1]
    if RULES.has_key(rule):
        rule = RULES[rule]
    try:
        player = cage.CursesPlayer(stdscr)
        map = cage.MooreMap(player.size)
        automaton = cage.TwoStateTotalisticAutomaton(map, rule)
        cage.RandomInitializer().initialize(automaton)
        player.main(automaton)
    finally:
        player.done()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print >> sys.stderr, "usage: %s <rule>" % sys.argv[0]
        sys.exit()
    curses.wrapper(main)
