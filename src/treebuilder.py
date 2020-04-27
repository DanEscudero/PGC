import sys
import os.path
from Node import Node
from util import list_subcategories

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
    (queryParameter, queryLevel, queryCMLimit) = state
    return '../out/' + queryParameter + '_' + str(queryLevel) + '_' + str(queryCMLimit)


def shouldBuildTree(state):
    return not os.path.isfile(getFilePath(state))


def main():
    # Read parameters from CLI
    argv = sys.argv[1:]
    argc = len(argv)

    if argc == 3:
        queryParameter = argv[0]
        queryLevel = int(argv[1])
        if (argv[2].isdigit()):
            queryCMLimit = int(argv[2])
        elif (argv[2].lower() == 'max'):
            queryCMLimit = 'max'
        else:
            raise Exception(
                'Invalid max value!. Please use: [0-9]+|\'max\' (limited to 500)')
    else:
        raise Exception('Invalid parameters!')

    state = (queryParameter, queryLevel, queryCMLimit)
    filepath = getFilePath(state)

    if (shouldBuildTree(state)):
        t = Node(queryParameter)
        buildTree(t, queryLevel, queryCMLimit)
        fp = open(filepath, 'w')
        t.dumpToFile(fp)
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
