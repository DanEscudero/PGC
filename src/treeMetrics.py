import sys
from treebuilder import shouldBuildTree, getFilePath
from Node import Node

# min: 0
# max: 4
# total: 16
# count1: 1
# count2: 2
# count3: 6
# count4: 7
#                  a
#        b                   c
#   d    e    f         g    h    i
#      j k l              m n o p


def sampleTree():
    a = Node('a')
    b = Node('b')
    c = Node('c')
    d = Node('d')
    e = Node('e')
    f = Node('f')
    g = Node('g')
    h = Node('h')
    i = Node('i')
    j = Node('j')
    k = Node('k')
    l = Node('l')
    m = Node('m')
    n = Node('n')
    o = Node('o')
    p = Node('p')

    a.addChild(b)
    a.addChild(c)

    b.addChild(d)
    b.addChild(e)
    b.addChild(f)

    c.addChild(g)
    c.addChild(h)
    c.addChild(i)

    d.addChild(j)
    d.addChild(k)
    d.addChild(l)

    h.addChild(m)
    h.addChild(n)
    h.addChild(o)
    h.addChild(p)

    filepath = '../out/sample'
    a.dumpToFile(open(filepath, 'w'))

    return a


def test():
    # t = sampleTree()
    t = Node.fromFile('../out/sample')

    return

    print('rc', t.recursiveCount())

    t_min = t.getMinChildren()
    print('min', t_min['count'], t_min['node'])

    t_max = t.getMaxChildren()
    print('max', t_max['count'], t_max['node'])

    for i in range(0, t.height):
        print('Total in level:', i, t.countInLevel(i))


def main():
    argv = sys.argv[1:]
    argc = len(argv)

    if argc == 2:
        queryParameter = argv[0]
        queryLevel = int(argv[1])
    else:
        raise Exception('Invalid parameters!')

    state = (queryParameter, queryLevel)

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

    total_per_levels = 0
    for i in range(0, t.height):
        total_i = t.countInLevel(i)
        total_per_levels += total_i
        print('Total in level:', i, total_i)

    print(total_per_levels)


if __name__ == "__main__":
    main()
