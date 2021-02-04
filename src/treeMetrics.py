import sys
from util import parse_args
from Node import Node


def main():
    state = parse_args(sys.argv)
    (queryParameter, _, _, _) = state

    if (Node.shouldBuildTree(state)):
        raise Exception('Tree should be built first!')

    t = Node.fromFile(Node.getFilePath(state))

    total = t.recursiveCount()
    t_max = t.maxChildren
    t_min = t.minChildren

    totals = []
    for i in range(0, t.height + 1):
        totals.append(t.countInLevel(i))

    totals.append(1)
    totals = totals[1:]
    totals.reverse()

    n_children = 0
    n_parents = 0
    avgs = []

    for i in range(0, len(totals)):
        if (i != 0):
            n_children = n_children + totals[i]

        if (i < len(totals) - 1):
            n_parents = n_parents + totals[i]

        if (i+1 < len(totals)):
            avg = totals[i+1] / totals[i]
            avgs.append("{:.1f}".format(avg))

    t_avg = n_children / n_parents

    print('\n === Tree Statistics: === ')
    print('Tree:        ', queryParameter)
    print('Height:      ', t.height)

    print('\n === Nodes Statistics: === ')
    print('Total Nodes: ', total)
    print('Min children:', t_min['count'])
    print('Avg Children:',"{:.1f}".format(t_avg))
    print('Max Children:', t_max['count'])

    print('\n === Statistics per level: ===')
    print('Avg nodes per level:', avgs)
    print('Nodes per level    :', totals)


if __name__ == "__main__":
    main()
