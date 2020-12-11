import sys
from Node import Node
from util import parse_args


def getRelevantTerms(state):
    filepath = '../out/extraction-short/' + Node.getFileName(state, True)

    fp = open(filepath)
    lines = fp.readlines()
    fp.close()
    return [x.strip() for x in lines]


def main():
    state = parse_args(sys.argv)
    relevantTerms = getRelevantTerms(state)
    print(relevantTerms)


if __name__ == "__main__":
    main()
