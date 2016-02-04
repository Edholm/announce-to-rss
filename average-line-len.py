#!/usr/bin/python
from sys import argv

lines = []
with open(argv[1], 'r') as f:
    lines = f.readlines()

lens = [len(x) for x in lines]

print(sum(lens) / len(lines))
