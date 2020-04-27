#!/bin/sh

echo "STARTING Neuroscience";
time -f'%E' python3 treebuilder.py "Neuroscience" 4 "max";

echo "STARTING Computer Science";
time -f'%E' python3 treebuilder.py "Computer Science" 4 "max";

echo "STARTING Pedagogy";
time -f'%E' python3 treebuilder.py "Pedagogy" 4 "max";
