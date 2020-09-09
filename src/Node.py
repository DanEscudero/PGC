import os.path
import functools
import jellyfish
from util import cleanTerm, invLerp, list_subcategories


class Node(object):
    SEPARATOR = ' $sep$ '
    SIMILARITY_LIMIT = 0.67

    def __init__(self, value, seq=0, parent=None):
        self.value = value
        self.parent = parent
        self.children = []
        self.seq = str(seq)

        self.cleanSearchedTerm = None

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
        self.__count = self.count
        self.__height = self.height
        self.__siblings = self.siblings
        self.__minChildren = self.minChildren
        self.__maxChildren = self.maxChildren
        self.__recursiveCount = self.recursiveCount()

        self.__freezed = True

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
        # TODO: modify as needed! Add children and parent
        return [self, self.parent] + self.children

    def getNeighborhoodWithScores(self):
        def assocNodeAndScore(node): return (node, node.getScore())
        return map(assocNodeAndScore, self.getNeighborhood())

    def getScore(self):
        # self.cleanSearchedTerm
        return (self.height, self.siblings, Node.getSiblingScore(self), Node.getTermMatchScore(self.cleanTermTokens, self.cleanSearchedTerm))

    def matches(self, searched):
        return Node.termMatch(searched, self.cleanTermTokens)

    def setCurrentlySearchedTerm(self, cleanSearchedTerm):
        self.cleanSearchedTerm = cleanSearchedTerm

        for child in self.children:
            child.setCurrentlySearchedTerm(cleanSearchedTerm)

    def lookForCurrentlySearchedTerm(self, accumulated=[]):
        self.assertLookingForSomething()

        if (self.matches(self.cleanSearchedTerm)):
            accumulated += self.getNeighborhoodWithScores()

        for child in self.children:
            child.lookForCurrentlySearchedTerm(accumulated)

        return accumulated

    def assertLookingForSomething(self):
        if (self.cleanSearchedTerm == None):
            msg = 'This node is currently looking for nothing! Make sure it\'s looking for something first.'
            raise Exception(msg)

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
            return Node.SEPARATOR
        else:
            return self.parent.value + Node.SEPARATOR + str(self.parent.seq)

    def writeSelfToFile(self, fp):
        args = [self.value, str(self.seq), self.getParentAsString()]
        line = Node.SEPARATOR.join(args)

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
        return line.split(Node.SEPARATOR)

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
    def termMatch(cleanSearchedTerm, treeTermTokens):
        score = Node.getTermMatchScore(cleanSearchedTerm, treeTermTokens)
        return score > Node.SIMILARITY_LIMIT

    # linear interpolation considering node's number of children between min and max children
    @staticmethod
    def getSiblingScore(node):
        minChildren = node.minChildren['count']
        maxChildren = node.maxChildren['count']
        return invLerp(minChildren, maxChildren, node.siblings)

    @staticmethod
    def getTermMatchScore(cleanTermTokens, cleanSearchedTerm):
        s1 = (' ').join(cleanTermTokens)
        s2 = (' ').join(cleanSearchedTerm)
        return jellyfish.jaro_winkler_similarity(s1, s2)

    @staticmethod
    def getFilePath(state):
        (queryParameter, _, queryLevel, queryCMLimit) = state
        return '../out/' + queryParameter + '_' + str(queryLevel) + '_' + str(queryCMLimit)

    @staticmethod
    def shouldBuildTree(state):
        return not os.path.isfile(Node.getFilePath(state))

    @staticmethod
    def buildTree(node, level, queryCMLimit):
        global seq
        subcategories = list_subcategories(node.value, queryCMLimit)
        for subcategory in subcategories:
            seq = seq + 1
            node.addChild(Node(subcategory, seq, node))

        if (level > 1):
            for child in node.children:
                Node.buildTree(child, level-1, queryCMLimit)

    @staticmethod
    def getFromInputState(state):
        filepath = Node.getFilePath(state)
        (queryParameter, _, queryLevel, queryCMLimit) = state

        if (Node.shouldBuildTree(state)):
            print('Starting build tree...')
            global seq
            seq = 0
            t = Node(queryParameter)
            Node.buildTree(t, queryLevel, queryCMLimit)
            t.dumpToFile(open(filepath, 'w'))
        else:
            print('Reading tree from file...')
            t = Node.fromFile(filepath)

        print('Tree built!')
        return t
