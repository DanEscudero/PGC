import sys
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
    (_, searchedTerm, _, _) = state
    cleanSearchedTerm = cleanTerm(searchedTerm)

    # t = Node('Algebra')
    # t.setCurrentlySearchedTerm(cleanSearchedTerm)
    # x = t.getTermMatchScore()
    # print(x)
    t = Node.getFromInputState(state)

    # TODO: benchmark freeze, to make compare it's effectiveness
    # t.freeze()

    t.setCurrentlySearchedTerm(cleanSearchedTerm)
    similarTerms = t.lookForCurrentlySearchedTerm()

    if (len(similarTerms) == 0):
        print('not found!')

    for term in similarTerms:
        (node, (h, s, x, k)) = term
        print(node.value, x, k)


if __name__ == "__main__":
    main()
