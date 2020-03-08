import sys
from Tree import Node
from util import list_subcategories

# Defaults
DEFAULT_QUERY_LEVEL = 1
DEFAULT_QUERY_PARAMETER = 'Mathematics'


def expandNode(node):
    subcategories = list_subcategories(node.value)

    for subcategory in subcategories:
        node.addChild(Node(subcategory))

    return node


def buildTree(node, level):
    expandNode(node)
    if (level > 1):
        for child in node.children:
            buildTree(child, level-1)


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

# t = Node(queryParameter)
# buildTree(t, queryLevel)

# x = t.findNode('asdasd')
# print(x)

t = Node.fromFile('../out/dump')
print(t)
