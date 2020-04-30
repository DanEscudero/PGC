#!/bin/sh

echo "STARTING Computer Science";
time -f'%E' python3 treeMetrics.py "Computer Science" 4 "max";

echo "STARTING Neuroscience";
time -f'%E' python3 treeMetrics.py "Neuroscience" 4 "max";

echo "STARTING Pedagogy";
time -f'%E' python3 treeMetrics.py "Pedagogy" 4 "max";
