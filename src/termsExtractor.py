import sys
from Node import Node
from util import parse_args, cleanTerm


def mapTermsToDict(terms):
    d = dict()
    for term in terms:
        (node, score) = term
        if (node not in d):
            d[node] = []
        d[node] += [score]

    return d


def getBestNode(values):
    maxScore = 0
    bestNode = None
    for value in values:
        (node, scores) = value
        score = scores[0]

        if (score > maxScore or bestNode == None):
            maxScore = score
            bestNode = node

    return bestNode


def extendWithNeighborhood(nodes):
    clean = []
    for node in nodes:
        clean += node.getNeighborhood()

    return clean


def sumarizeAndOrderNodes(nodesWithScores):
    return sorted(
        nodesWithScores.items(),
        key=lambda x: sum(x[1]),
        reverse=True
    )


def main():
    state = parse_args(sys.argv)
    (_, searchedTerm, _, _) = state
    cleanSearchedTerm = cleanTerm(searchedTerm)

    t = Node.getFromInputState(state)

    # TODO: benchmark freeze, to check it's effectiveness
    # t.freeze()

    t.setCurrentlySearchedTerm(cleanSearchedTerm)
    goodNodes = t.getGoodNodes()
    goodNodes = extendWithNeighborhood(goodNodes)

    if (len(goodNodes) == 0):
        print('not found!')

    goodNodes = Node.initializeScores(goodNodes)
    Node.addScores(goodNodes, Node.getTermScore)
    bestNode = getBestNode(goodNodes)

    Node.addScores(goodNodes, lambda x: Node.getSimilarityBetween(x, bestNode))
    goodNodes = Node.combineScores(goodNodes)

    dictNodes = mapTermsToDict(goodNodes)
    sortedNodes = sumarizeAndOrderNodes(dictNodes)

    filepath = '../out/extraction-full/' + Node.getFileName(state, True)
    fp = open(filepath, 'w')
    for item in sortedNodes:
        (term, scores) = item
        fp.write(term + '\n')
        for score in scores:
            fp.write('\t' + str(score) + '\n')

    fp.close()

    filepath = '../out/extraction-short/' + Node.getFileName(state, True)
    fp = open(filepath, 'w')
    for item in sortedNodes:
        (term, scores) = item
        fp.write(term + '\n')

    fp.close()


if __name__ == "__main__":
    main()
