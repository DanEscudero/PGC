import functools


class Node(object):
    def __init__(self, value):
        self.value = value
        self.children = []

    def __str__(self):
        s = 'Node: ' + self.value + '\n'
        s += 'Children: ' + \
            (', ').join(map(lambda x: x.value, self.children)) + '\n'
        return s

    def findNode(self, value):
        if (self.value == value):
            return self

        for child in self.children:
            if (child.findNode(value) != None):
                return child

        return None

    @property
    def count(self):
        return len(self.children)

    @property
    def recursiveCount(self):
        return functools.reduce(lambda a, b: a+b, map(lambda x: x.recursiveCount, self.children), self.count)

    @property
    def height(self):
        if not self.count:
            return 0

        maxHeight = 0
        for child in self.children:
            maxHeight = max(maxHeight, child.height)

        return 1 + maxHeight

    def addChild(self, obj):
        self.children.append(obj)
        return obj

    # TODO: reduce n^n complexity is necessary?
    @staticmethod
    def fromFile(filepath):
        with open(filepath) as f:
            lines = list(map(lambda x: x[:-1], f.readlines()))

        [name, parent] = lines[0].split(',')
        if (parent == ''):
            t = Node(name)

        t = Node(name)
        for line in lines[1:]:
            [name, parentValue] = line.split(',')
            parent = t.findNode(parentValue)

            if (parent == None):
                print('invalid tree')
                exit(-1)

            parent.addChild(Node(name))

        return t
