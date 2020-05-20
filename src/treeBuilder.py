import sys
import os.path
from Node import Node
from util import list_subcategories, parse_args

# Defaults
DEFAULT_QUERY_LEVEL = 3
DEFAULT_QUERY_PARAMETER = 'Mathematics'
DEFAULT_QUERY_PARAMETER = 'max'
seq = 0


def buildTree(node, level, queryCMLimit):
    global seq
    subcategories = list_subcategories(node.value, queryCMLimit)
    for subcategory in subcategories:
        seq = seq + 1
        node.addChild(Node(subcategory, seq, node))

    if (level > 1):
        for child in node.children:
            buildTree(child, level-1, queryCMLimit)


def getFilePath(state):
    (queryParameter, specificParameter, queryLevel, queryCMLimit) = state
    return '../out/' + queryParameter + '_' + str(queryLevel) + '_' + str(queryCMLimit)


def shouldBuildTree(state):
    return not os.path.isfile(getFilePath(state))


def main():
    # Read parameters from CLI
    state = parse_args(sys.argv)
    filepath = getFilePath(state)

    (queryParameter, _, queryLevel, queryCMLimit) = state

    if (shouldBuildTree(state)):
        t = Node(queryParameter)
        buildTree(t, queryLevel, queryCMLimit)
        t.dumpToFile(open(filepath, 'w'))
    else:
        t = Node.fromFile(filepath)

    print('Tree:   ', queryParameter)
    print('Height: ', t.height)

    total_per_levels = 0
    for i in range(0, t.height):
        total_i = t.countInLevel(i)
        total_per_levels += total_i
        print('Total in level:', i, total_i)

    print(total_per_levels)


if __name__ == "__main__":
    main()
