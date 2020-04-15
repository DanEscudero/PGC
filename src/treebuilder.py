import sys
import os.path
from Node import Node
from util import list_subcategories

# Defaults
DEFAULT_QUERY_LEVEL = 3
DEFAULT_QUERY_PARAMETER = 'Mathematics'
DEFAULT_QUERY_PARAMETER = 'max'


def expandNode(node):
    subcategories = list_subcategories(node.value)

    for subcategory in subcategories:
        node.addChild(Node(subcategory, node))

    return node


def buildTree(node, level):
    print('level>', level)
    expandNode(node)
    if (level > 1):
        for child in node.children:
            buildTree(child, level-1)


def getFilePath(state):
    (queryParameter, queryLevel) = state
    return '../out/' + queryParameter + '_' + str(queryLevel)


def shouldBuildTree(state):
    return not os.path.isfile(getFilePath(state))


def main():
    print("hello world!")

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

    state = (queryParameter, queryLevel)
    filepath = getFilePath(state)

    if (shouldBuildTree(state)):
        t = Node(queryParameter, None)
        buildTree(t, queryLevel)
        fp = open(filepath, 'w')
        t.dumpToFile(fp)
    else:
        t = Node.fromFile(filepath)


if __name__ == "__main__":
    main()
