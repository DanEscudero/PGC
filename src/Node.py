import functools
import itertools
from util import cleanTerm

SEPARATOR = ' $sep$ '


class Node(object):
    def __init__(self, value, seq=0, parent=None):
        self.value = value
        # keep clean term can make searches faster down the way
        self.clearTermTokens = cleanTerm(value)
        self.parent = parent
        self.children = []
        self.seq = str(seq)

    def __str__(self):
        if (self.parent == None):
            parent = ''
        else:
            parent = self.parent.value

        s = 'Parent  : ' + parent + '\n'
        s += 'Node    : ' + self.value + '\n'
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

    # terms comparison function, returns bool
    @staticmethod
    def termMatch(clean_searched_term, tree_clean):
        def join(p): return (' ').join(p)
        def perms(term): return list(map(join, itertools.permutations(term)))

        # supposing tree_clean is ['a', 'b', 'c'], tree_permutations is ['a b c', 'a c b', 'b a c', ...]
        tree_permutations = perms(tree_clean)
        search_permutations = perms(clean_searched_term)

        # check if any permutation of one of the terms is a substring of another one
        for tree_permutation in tree_permutations:
            for search_permutation in search_permutations:
                if (tree_permutation in search_permutation or search_permutation in tree_permutation):
                    return True

        return False

    # must return list
    @staticmethod
    def getNeighborhood(t):
        return [t, t.parent] + t.children

    # search_clean is assumed to have passed through cleanTerm
    def lookForTerm(self, clean_searched_term, accumulated=[]):
        if (Node.termMatch(clean_searched_term, self.clearTermTokens)):
            neighborhood = Node.getNeighborhood(self)
            accumulated += neighborhood

        for child in self.children:
            child.lookForTerm(clean_searched_term, accumulated)

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

    def countChildrenUpToLevel(self, l):
        return -1

    def addChild(self, obj):
        for child in self.children:
            if (child.value == obj.value):
                return

        self.children.append(obj)
        obj.parent = self

    def dumpToFile(self, fp):
        self.writeSelfToFile(fp)

        for child in self.children:
            child.dumpToFile(fp)

    def getParentAsString(self):
        if (self.parent == None):
            return SEPARATOR
        else:
            return self.parent.value + SEPARATOR + str(self.parent.seq)

    def writeSelfToFile(self, fp):
        args = [self.value, str(self.seq), self.getParentAsString()]
        line = SEPARATOR.join(args)

        fp.write(line + '\n')

    @staticmethod
    def fromFile(filepath):
        lines = Node.getLinesFromFile(filepath)

        [name, seq, parent, _] = Node.unpatchLine(lines[0])

        # If there's no parent, create tree
        if (parent == ''):
            t = Node(name, seq, None)

        for line in lines[1:]:
            Node.addLineToTree(line, t)

        return t

    @staticmethod
    def unpatchLine(line):
        return line.split(SEPARATOR)

    @staticmethod
    def handleInvalidTree(t):
        print(t)
        print('invalid tree')
        exit(-1)

    @staticmethod
    def getLinesFromFile(filepath):
        f = open(filepath)
        lines = list(map(lambda x: x[:-1], f.readlines()))  # remove '\n'
        f.close()

        return lines

    @staticmethod
    def addLineToTree(line, t):
        [name, seq, parentValue, parentSeq] = Node.unpatchLine(line)
        parent = t.findNode(parentValue, parentSeq)

        if (parent == None):
            Node.handleInvalidTree(t)

        newNode = Node(name, seq, parent)
        parent.addChild(newNode)
