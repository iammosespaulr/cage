import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cage",
    version = "1.1.4",
    author = " Erik Max Francis ",
    author_email = "max@alcyone.com",
    description = ('CAGE is a fairy generic and complete cellular automaton simulation engine in Python.'),
    license = "LGPL",
    keywords = "python cellular automata simulation engine",
    url = "http://www.alcyone.com/software/cage/",
    packages=['cage'],
    long_description=read('cage/README'),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: LGPL License",
    ],
)
