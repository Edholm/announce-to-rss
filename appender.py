#!/usr/bin/env python
import sys
import random

line = None
with open(sys.argv[2], 'r') as f:
    lines = f.readlines()
    line = lines[random.randint(0, len(lines))]


with open(sys.argv[1], 'a') as f:
    f.write(line)
