import sys
from treeBuilder import shouldBuildTree, getFilePath
from util import parse_args, cleanTerm
from Node import Node


def main():
    state = parse_args(sys.argv)
    (queryParameter, specificTerm, queryLevel, queryCMLimit) = state
    clean_term = cleanTerm(specificTerm)

    filepath = getFilePath(state)

    if (shouldBuildTree(state)):
        raise Exception('Tree should be built first!')

    t = Node.fromFile(getFilePath(state))

    terms = []
    t = t.lookForTerm(clean_term, terms)
    print(clean_term)

    if (len(terms) == 0):
        print('not found!')

    for term in terms:
        print(term.value)


if __name__ == "__main__":
    main()
