import sys
import os.path
from Node import Node
from util import list_subcategories

# Defaults
DEFAULT_QUERY_LEVEL = 3
DEFAULT_QUERY_PARAMETER = 'Mathematics'


def expandNode(node):
    subcategories = list_subcategories(node.value)

    for subcategory in subcategories:
        node.addChild(Node(subcategory, node))

    return node


def buildTree(node, level):
    expandNode(node)
    if (level > 1):
        for child in node.children:
            buildTree(child, level-1)


def getFilePath(state):
    (queryParameter, queryLevel) = state
    return '../out/' + queryParameter + '_' + str(queryLevel)


def shouldBuildTree(state):
    return not os.path.isfile(getFilePath(state))


# Read parameters from CLI
argv = sys.argv[1:]
argc = len(argv)

if argc == 2:
    queryLevel = int(argv[1])
    queryParameter = argv[0]
else:
    # TODO: throw error and explain required input
    queryLevel = DEFAULT_QUERY_LEVEL
    queryParameter = DEFAULT_QUERY_PARAMETER

state = (queryParameter, queryLevel)
filepath = getFilePath(state)

if (shouldBuildTree(state)):
    t = Node(queryParameter, None)
    buildTree(t, queryLevel)
    fp = open(filepath, 'w')
    t.dumpToFile(fp)
else:
    t = Node.fromFile(filepath)

print('ok!')
print(t)
print(t.height)
print(t.recursiveCount)
