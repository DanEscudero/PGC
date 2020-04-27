import functools

SEPARATOR = ' $sep$ '


class Node(object):
    def __init__(self, value, seq=0, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        self.seq = str(seq)

    def __str__(self):
        if (self.parent == None):
            parent = ''
        else:
            parent = self.parent.value

        s = 'Node: ' + self.value + '\n'
        s += 'Parent: ' + parent + '\n'
        s += 'Children: ' + \
            (', ').join(map(lambda x: x.value, self.children)) + '\n'
        return s

    def findNode(self, value, seq):
        if (str(self.seq) == str(seq) and self.value == value):
            return self

        for child in self.children:
            found = child.findNode(value, seq)
            if (found != None):
                return found

        return None

    @property
    def count(self):
        return len(self.children)

    def recursiveCount(self, acc=1):
        return acc + functools.reduce(lambda a, b: a+b, map(lambda x: x.recursiveCount(acc=0), self.children), self.count)

    @property
    def height(self):
        if not self.count:
            return 0

        maxHeight = 0
        for child in self.children:
            maxHeight = max(maxHeight, child.height)

        return 1 + maxHeight

    def getMaxChildren(self):
        children = list(map(lambda x: x.getMaxChildren(), self.children))
        children.append({"count": self.count, "node": self})

        return max(children, key=lambda x: x['count'])

    def countInLevel(self, level):
        if (self.height == level):
            child_sum = self.count
        else:
            child_sum = 0
            for child in self.children:
                child_sum = child_sum + child.countInLevel(level)

        return child_sum

    def getAvgChildren(self):
        return self.countInLevel(2)

    def getMinChildren(self):
        children = list(map(lambda x: x.getMinChildren(), self.children))
        children.append({"count": self.count, "node": self})

        return min(children, key=lambda x: x['count'])

    def getChildrenPerLevel(self):
        return -1

    def countChildrenUpToLevel(l):
        return -1

    def addChild(self, obj):
        for child in self.children:
            if (child.value == obj.value):
                return

        self.children.append(obj)
        obj.parent = self

    # TODO: reduce n*log(n) complexity is necessary?
    @staticmethod
    def fromFile(filepath):
        with open(filepath) as f:
            lines = list(map(lambda x: x[:-1], f.readlines()))  # remove '\n'
            f.close()

        [name, seq, parent, parent_seq] = lines[0].split(SEPARATOR)
        if (parent == ''):
            t = Node(name, seq, None)

        for line in lines[1:]:
            [name, seq, parentValue, parentSeq] = line.split(SEPARATOR)
            parent = t.findNode(parentValue, parentSeq)

            if (parent == None):
                print(t)
                print('invalid tree')
                exit(-1)

            parent.addChild(Node(name, seq, parent))

        return t

    def dumpToFile(self, fp):
        if (self.parent == None):
            parent = SEPARATOR
        else:
            parent = self.parent.value + SEPARATOR + str(self.parent.seq)

        value = self.value + SEPARATOR + str(self.seq)
        fp.write(value + SEPARATOR + parent + '\n')

        for child in self.children:
            child.dumpToFile(fp)
