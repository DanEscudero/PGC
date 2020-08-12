import sys
from treeBuilder import shouldBuildTree, getFilePath
from util import parse_args
from Node import Node
import random


def main():
    state = parse_args(sys.argv)
    (queryParameter, _, queryLevel, queryCMLimit) = state
    filepath = getFilePath(state)

    if (shouldBuildTree(state)):
        raise Exception('Tree should be built first!')

    t = Node.fromFile(getFilePath(state))

    print('Tree:   ', queryParameter)
    print('Height: ', t.height)

    total = t.recursiveCount()
    # t_max = t.getMaxChildren()
    t_min = t.getMinChildren()
    print(t_min)

    # print('T:      ', total)
    # print('T_max:  ', {"count": t_max['count'], "node": t_max['node'].value})
    # print('T_min:  ', {
    #       "count": t_min['count'], "node": t_min['node'].value, "height": t_min.height})

    totals = []
    for i in range(0, t.height + 1):
        totals.append(t.countInLevel(i))

    totals.append(1)
    totals = totals[1:]
    totals.reverse()

    n_children = 0
    n_parents = 0

    for i in range(0, len(totals)):
        if (i != 0):
            n_children = n_children + totals[i]

        if (i < len(totals) - 1):
            n_parents = n_parents + totals[i]

        if (i+1 < len(totals)):
            avg = totals[i+1] / totals[i]
            print('average ' + str(i+1) + ':',  "{:.1f}".format(avg))

    # t_avg = n_children / n_parents
    # print('T:      ', total)
    # print('T_min:  ', t_min['count'])
    # print('T_avg:  ',   "{:.1f}".format(t_avg))
    # print('T_max:  ', t_max['count'])
    # print(totals)


if __name__ == "__main__":
    main()
