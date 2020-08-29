import functools
import itertools
from util import cleanTerm, invLerp

SEPARATOR = ' $sep$ '


class Node(object):
    def __init__(self, value, seq=0, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        self.seq = str(seq)

        self.__freezed = False

        self.__count = None
        self.__height = None
        self.__siblings = None
        self.__minChildren = None
        self.__maxChildren = None
        self.__recursiveCount = None

        # keep clean term can make searches faster down the way
        self.cleanTermTokens = cleanTerm(value)

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

    @property
    def count(self):
        if (self.__freezed):
            return self.__count

        return len(self.children)

    @property
    def siblings(self):
        if (self.__freezed):
            return self.__siblings

        if (self.parent == None):
            return 1
        else:
            return self.parent.count

    @property
    def height(self):
        if (self.__freezed):
            return self.__height

        if not self.count:
            return 0

        maxHeight = 0
        for child in self.children:
            maxHeight = max(maxHeight, child.height)

        return 1 + maxHeight

    @property
    def minChildren(self):
        if (self.__freezed):
            return self.__minChildren

        children = list(map(lambda x: x.minChildren, self.children))
        children.append({"count": self.count, "node": self})

        return min(children, key=lambda x: x['count'])

    @property
    def maxChildren(self):
        if (self.__freezed):
            return self.__maxChildren

        children = list(map(lambda x: x.maxChildren, self.children))
        children.append({"count": self.count, "node": self})

        return max(children, key=lambda x: x['count'])

    # Freezing node saves all properties, so it has constant time to access.
    # Otherwise, time required to calculate is significantly increased
    def freeze(self):
        self.__freezed = True

        self.__count = self.count
        self.__height = self.height
        self.__siblings = self.siblings
        self.__minChildren = self.minChildren
        self.__maxChildren = self.maxChildren
        self.__recursiveCount = self.recursiveCount()

        for child in self.children:
            child.freeze()

    def unfreeze(self):
        self.__freezed = False

        self.__count = None
        self.__height = None
        self.__siblings = None
        self.__minChildren = None
        self.__maxChildren = None
        self.__recursiveCount = None

        for child in self.children:
            child.unfreeze()

    def findNode(self, value, seq):
        if (str(self.seq) == str(seq) and self.value == value):
            return self

        for child in self.children:
            found = child.findNode(value, seq)
            if (found != None):
                return found

        return None

    def getNeighborhood(self):
        return [self]

    def getNeighborhoodWithScores(self):
        neighborhood = self.getNeighborhood()
        return map(lambda x: (x, x.getScore()), neighborhood)

    def getScore(self):
        return (self.height, self.siblings, self.getSiblingScore())

    def getSiblingScore(self):
        minChildren = self.minChildren['count']
        maxChildren = self.maxChildren['count']
        return invLerp(minChildren, maxChildren, self.siblings)

    def matches(self, searched):
        return Node.termMatch(searched, self.cleanTermTokens)

    # search_clean is assumed to have passed through cleanTerm
    def lookForTerm(self, cleanSearchedTerm, accumulated=[]):
        if (self.matches(cleanSearchedTerm)):
            neighborhood = self.getNeighborhoodWithScores()
            accumulated += neighborhood

        for child in self.children:
            child.lookForTerm(cleanSearchedTerm, accumulated)

        return accumulated

    def recursiveCount(self, acc=1):
        if (self.__freezed):
            return self.__recursiveCount
        return acc + functools.reduce(lambda a, b: a+b, map(lambda x: x.recursiveCount(acc=0), self.children), self.count)

    def countInLevel(self, level):
        if (self.height == level):
            child_sum = self.count
        else:
            child_sum = 0
            for child in self.children:
                child_sum = child_sum + child.countInLevel(level)

        return child_sum

    def addChild(self, obj):
        if (self.__freezed):
            raise Exception('Cant modify freezed tree!')

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
