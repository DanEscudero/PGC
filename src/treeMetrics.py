import sys
from treebuilder import shouldBuildTree, getFilePath
from Node import Node

argv = sys.argv[1:]
argc = len(argv)

if argc == 2:
    queryParameter = argv[0]
    queryLevel = int(argv[1])
else:
    raise Exception('Invalid parameters!')

state = (queryParameter, queryLevel)

if (shouldBuildTree(state)):
    raise Exception('Tree should be built first!')

t = Node.fromFile(getFilePath(state))

print('Tree: ', queryParameter)
print('T: ', t.recursiveCount)
print('T_min: ', t.getMaxChildren())
print('T_med: ', t.getAvgChildren())
print('T_max: ', t.getMinChildren())
