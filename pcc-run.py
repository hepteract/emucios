#!/usr/bin/python2

from marshal import loads
from sys import argv

with open(argv[1]) as f:
    code = f.read()

exec loads( code[1:] )
