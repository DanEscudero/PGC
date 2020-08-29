import sys
from treeBuilder import shouldBuildTree, getFilePath
from util import parse_args, cleanTerm, pp_json
from Node import Node


def mapTermsToDict(terms):
    d = dict()
    for term in terms:
        (node, score) = term
        key = node.value

        if (key in d):
            d[key].append(score)
        else:
            d[key] = [score]

    return d


def main():
    state = parse_args(sys.argv)
    (_, specificTerm, _, _) = state

    if (shouldBuildTree(state)):
        raise Exception('Tree should be built first!')

    t = Node.fromFile(getFilePath(state))

    similarTerms = t.lookForTerm(cleanTerm(specificTerm))

    if (len(similarTerms) == 0):
        print('not found!')

    scoresPerTerm = mapTermsToDict(similarTerms)
    pp_json(scoresPerTerm)

    for term in similarTerms:
        (value, (h, s)) = term
        print(value.value, h, s)


if __name__ == "__main__":
    main()
