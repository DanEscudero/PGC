import sys
import itertools
import jellyfish
import numpy as np
from Node import Node
from util import parse_args, cleanTerm, pp_json


def mapTermsToDict(terms):
    d = dict()
    for term in terms:
        (node, score) = term
        key = node.value

        d[key] = score

    return d


def main():
    state = parse_args(sys.argv)
    (_, searchedTerm, _, _) = state
    cleanSearchedTerm = cleanTerm(searchedTerm)

    t = Node.getFromInputState(state)

    # TODO: benchmark freeze, to make compare it's effectiveness
    # t.freeze()

    t.setCurrentlySearchedTerm(cleanSearchedTerm)
    similarTerms = t.lookForCurrentlySearchedTerm()

    if (len(similarTerms) == 0):
        print('not found!')

    similarTerms = set(similarTerms)
    similarTerms = mapTermsToDict(similarTerms)
    similarTerms = sorted(similarTerms.items(),
                          key=lambda x: x[1][3], reverse=True)
    for value in similarTerms:
        (term, (h, s, siblingScore, termScore)) = value
        print(term, round(termScore, 2))
        # print(' siblingScore:', siblingScore)
        # print('    termScore:', termScore)
        # print('')

    print(len(similarTerms))


if __name__ == "__main__":
    main()
