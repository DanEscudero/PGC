import sys
from treeBuilder import shouldBuildTree, getFilePath
from util import parse_args, cleanTerm
from Node import Node


def main():
    state = parse_args(sys.argv)
    (_, specificTerm, _, _) = state
    clean_term = cleanTerm(specificTerm)

    filepath = getFilePath(state)

    if (shouldBuildTree(state)):
        raise Exception('Tree should be built first!')

    t = Node.fromFile(getFilePath(state))

    terms = []
    t = t.lookForTerm(clean_term, terms)

    if (len(terms) == 0):
        print('not found!')

    values = list(set(map(lambda x: x.value, terms)))
    for value in values:
        print(value)


if __name__ == "__main__":
    main()
