import sys
from treebuilder import shouldBuildTree, getFilePath
from util import parse_args
from Node import Node


def main():
    state = parse_args(sys.argv)
    (queryParameter, queryLevel, queryCMLimit) = state
    filepath = getFilePath(state)

    if (shouldBuildTree(state)):
        raise Exception('Tree should be built first!')

    t = Node.fromFile(getFilePath(state))

    print('Tree:   ', queryParameter)
    print('Height: ', t.height)

    total = t.recursiveCount()
    t_max = t.getMaxChildren()
    t_min = t.getMinChildren()

    print('T:      ', total)
    print('T_max:  ', {"count": t_max['count'], "node": t_max['node'].value})
    print('T_min:  ', {"count": t_min['count'], "node": t_min['node'].value})

    totals = []
    for i in range(0, t.height + 1):
        totals.append(t.countInLevel(i))

    totals.append(1)
    totals = totals[1:]
    totals.reverse()

    for i in range(0, len(totals)):
        if (i+1 < len(totals)):
            avg = totals[i+1] / totals[i]
            print('avg:', "{:.1f}".format(avg))


if __name__ == "__main__":
    main()
