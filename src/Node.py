import functools


class Node(object):
    def __init__(self, value, parent):
        self.value = value
        self.parent = parent
        self.children = []

    def __str__(self):
        if (self.parent == None):
            parent = ''
        else:
            parent = self.parent.value

        s = 'Node: ' + self.value + '\n'
        s = 'Parent: ' + parent + '\n'
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

    # TODO: reduce n*log(n) complexity is necessary?
    @staticmethod
    def fromFile(filepath):
        with open(filepath) as f:
            lines = list(map(lambda x: x[:-1], f.readlines()))  # remove '\n'
            f.close()

        [name, parent] = lines[0].split(' $sep$ ')
        if (parent == ''):
            t = Node(name, None)

        for line in lines[1:]:
            [name, parentValue] = line.split(' $sep$ ')
            parent = t.findNode(parentValue)

            if (parent == None):
                print('invalid tree')
                exit(-1)

            parent.addChild(Node(name, parent))

        return t

    def dumpToFile(self, fp):
        if (self.parent == None):
            parent = ''
        else:
            parent = self.parent.value

        fp.write(self.value + ' $sep$ ' + parent + '\n')

        for child in self.children:
            child.dumpToFile(fp)
